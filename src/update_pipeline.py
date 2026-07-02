import os
import glob
import pandas as pd

from quality_checks import (
    validar_no_vacio,
    validar_columnas,
    validar_tipos_y_nulos_basicos,
    validar_rangos_ventas,
    warning_outliers_iqr,
    validar_duplicados
)

from kpi import agregar_kpis_vs_promedio, resumen_kpis
from logging_setup import get_logger
from reporting import generar_graficas_y_insights
from email_report import generar_reporte_html
from generar_presupuesto import generar_presupuesto

RAW_DIR = "data/raw"
HIST_PATH = "data/processed/ventas_historico.csv"
PRESUP_PATH = "data/processed/presupuesto_ventas.csv"

OUT_XLSX = "output/kpi_daily.xlsx"
OUT_CSV = "output/kpi_daily.csv"
OUT_MODELO = "output/modelo_dashboard.csv"
OUT_VS_PRESUP = "output/ventas_vs_presupuesto.csv"
OUT_RESUMEN_PRESUP = "output/resumen_presupuesto.csv"


def cargar_historico():
    if os.path.exists(HIST_PATH):
        df = pd.read_csv(HIST_PATH)
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        return df
    return pd.DataFrame(columns=["fecha", "region", "producto", "ventas"])


def guardar_historico(df):
    os.makedirs(os.path.dirname(HIST_PATH), exist_ok=True)
    df.to_csv(HIST_PATH, index=False)


def listar_archivos_raw():
    os.makedirs(RAW_DIR, exist_ok=True)
    return sorted(glob.glob(os.path.join(RAW_DIR, "ventas_*.csv")))


def cargar_raw(archivos):
    frames = []
    for f in archivos:
        d = pd.read_csv(f)
        frames.append(d)

    if not frames:
        return pd.DataFrame(columns=["fecha", "region", "producto", "ventas"])

    df = pd.concat(frames, ignore_index=True)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df


def cargar_presupuesto():
    if os.path.exists(PRESUP_PATH):
        df = pd.read_csv(PRESUP_PATH)
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        return df
    return pd.DataFrame(columns=["fecha", "venta_presupuestada"])


def reemplazar_fechas_en_historico(hist, raw):
    """
    Elimina del histórico cualquier fecha presente en raw
    y luego concatena únicamente la nueva carga para esas fechas.
    De esta forma, el pipeline queda blindado contra reprocesamientos
    del mismo día.
    """
    if raw.empty:
        return hist.copy()

    if hist.empty:
        return raw.copy()

    fechas_raw = raw["fecha"].dropna().dt.normalize().unique()

    hist_base = hist[~hist["fecha"].dt.normalize().isin(fechas_raw)].copy()

    combinado = pd.concat(
        [
            hist_base[["fecha", "region", "producto", "ventas"]],
            raw[["fecha", "region", "producto", "ventas"]],
        ],
        ignore_index=True
    )

    return combinado


def warning_volumen_por_fecha(df, logger, umbral=250):
    """
    Warning preventivo para detectar días con un volumen de filas anómalo.
    No frena el pipeline; solo deja trazabilidad en el log.
    """
    if df.empty:
        return

    conteo = df.groupby(df["fecha"].dt.normalize()).size()
    fechas_altas = conteo[conteo > umbral]

    if not fechas_altas.empty:
        logger.warning("⚠️ Fechas con volumen de filas superior al umbral:")
        for fecha, cantidad in fechas_altas.items():
            logger.warning(f"   - {fecha.strftime('%Y-%m-%d')}: {cantidad} filas")


def calcular_ventas_vs_presupuesto(df_historico, df_presupuesto):
    """
    Agrega ventas reales por día y las compara contra el presupuesto diario.
    Devuelve:
      - df_vs_presup: tabla diaria con ventas, presupuesto, desvío y desvío %
      - resumen: dict con métricas de negocio
    """
    if df_historico.empty:
        return pd.DataFrame(), {}

    # ventas reales por día
    ventas_diarias = (
        df_historico.groupby("fecha", as_index=False)["ventas"]
        .sum()
        .rename(columns={"ventas": "ventas_reales"})
    )

    if df_presupuesto.empty:
        df_vs_presup = ventas_diarias.copy()
        df_vs_presup["venta_presupuestada"] = pd.NA
        df_vs_presup["desvio"] = pd.NA
        df_vs_presup["desvio_pct"] = pd.NA
        return df_vs_presup, {}

    # merge diario
    df_vs_presup = ventas_diarias.merge(df_presupuesto, on="fecha", how="left")

    # cálculos
    df_vs_presup["desvio"] = df_vs_presup["ventas_reales"] - df_vs_presup["venta_presupuestada"]

    df_vs_presup["desvio_pct"] = df_vs_presup["desvio"] / df_vs_presup["venta_presupuestada"]
    df_vs_presup.loc[df_vs_presup["venta_presupuestada"].isna(), "desvio_pct"] = pd.NA
    df_vs_presup.loc[df_vs_presup["venta_presupuestada"] == 0, "desvio_pct"] = pd.NA

    # resumen
    df_valid = df_vs_presup.dropna(subset=["venta_presupuestada"]).copy()

    if df_valid.empty:
        return df_vs_presup, {}

    peor_dia = df_valid.sort_values("desvio", ascending=True).iloc[0]
    mejor_dia = df_valid.sort_values("desvio", ascending=False).iloc[0]

    resumen = {
        "ventas_reales_total": float(df_valid["ventas_reales"].sum()),
        "venta_presupuestada_total": float(df_valid["venta_presupuestada"].sum()),
        "desvio_total": float(df_valid["desvio"].sum()),
        "desvio_promedio": float(df_valid["desvio"].mean()),
        "pct_dias_sobre_presupuesto": float((df_valid["desvio"] > 0).mean() * 100),
        "mejor_dia_fecha": mejor_dia["fecha"].strftime("%Y-%m-%d"),
        "mejor_dia_desvio": float(mejor_dia["desvio"]),
        "peor_dia_fecha": peor_dia["fecha"].strftime("%Y-%m-%d"),
        "peor_dia_desvio": float(peor_dia["desvio"]),
    }

    return df_vs_presup, resumen


def main():
    logger = get_logger("update_pipeline", "logs/pipeline.log")
    os.makedirs("output", exist_ok=True)

    
    logger.info("🔄 Generando presupuesto dinámico")
    generar_presupuesto()
    logger.info("✅ Presupuesto actualizado")


    # 1) listar archivos entrantes
    archivos = listar_archivos_raw()
    if not archivos:
        logger.warning("⚠️ No hay archivos en data/raw. Genera uno con: python src/run_generate_daily.py")
        return

    # 2) cargar histórico y raw
    hist = cargar_historico()
    raw = cargar_raw(archivos)

    # logging de fechas entrantes
    fechas_raw = sorted(raw["fecha"].dropna().dt.strftime("%Y-%m-%d").unique().tolist())
    logger.info(f"📥 Fechas entrantes en RAW: {fechas_raw}")
    logger.info(f"📦 Filas RAW antes de validar: {len(raw)}")

    # eliminar duplicados exactos antes de validar
    raw = raw.drop_duplicates(subset=["fecha", "region", "producto", "ventas"])

    # 3) validaciones de entrada
    validar_no_vacio(raw, "RAW (data/raw)")
    validar_columnas(raw, ["fecha", "region", "producto", "ventas"], "RAW (data/raw)")

    # Convertimos tipos y validamos nulos
    raw = validar_tipos_y_nulos_basicos(raw, "RAW (data/raw)")

    # Rango razonable
    validar_rangos_ventas(raw, min_ok=1, max_ok=200000, nombre="RAW (data/raw)")

    # Duplicados (después del drop deberían ser 0)
    validar_duplicados(raw, subset=["fecha", "region", "producto", "ventas"], nombre="RAW (data/raw)")

    # Outliers como warning
    warning_outliers_iqr(raw, "RAW (data/raw)")

    # 4) reemplazar en histórico las fechas presentes en raw
    logger.info(f"📚 Filas histórico previas: {len(hist)}")
    combinado = reemplazar_fechas_en_historico(hist, raw)

    # deduplicación técnica adicional (por seguridad)
    combinado = combinado.drop_duplicates(subset=["fecha", "region", "producto", "ventas"])
    logger.info(f"🧩 Filas combinadas después de reemplazar fechas: {len(combinado)}")

    # warning preventivo de volúmenes anómalos
    warning_volumen_por_fecha(combinado, logger, umbral=250)

    # 5) calcular KPI base
    combinado = agregar_kpis_vs_promedio(combinado)

    # validar columnas post KPI
    validar_columnas(
        combinado,
        ["promedio_producto", "venta_sobre_prom_producto", "promedio_region", "venta_sobre_prom_region"],
        "COMBINADO (post-KPI)"
    )

    # 6) guardar histórico actualizado
    guardar_historico(combinado)

    # 7) generar reportes KPI
    res = resumen_kpis(combinado)

    # 8) generar modelo BI para Power BI
    cols_modelo = [
        "fecha",
        "region",
        "producto",
        "ventas",
        "promedio_producto",
        "venta_sobre_prom_producto",
        "promedio_region",
        "venta_sobre_prom_region"
    ]

    modelo = combinado[cols_modelo].copy()
    modelo.to_csv(OUT_MODELO, index=False)
    logger.info("✅ modelo_dashboard.csv actualizado para Power BI")
    logger.debug(f"Keys disponibles en res: {list(res.keys())}")

    # 9) integración ventas vs presupuesto
    presupuesto = cargar_presupuesto()

    if presupuesto.empty:
        logger.warning(f"⚠️ No se encontró presupuesto en {PRESUP_PATH}. Se omite análisis vs presupuesto.")
    else:
        validar_no_vacio(presupuesto, "PRESUPUESTO")
        validar_columnas(presupuesto, ["fecha", "venta_presupuestada"], "PRESUPUESTO")

        presupuesto["venta_presupuestada"] = pd.to_numeric(
            presupuesto["venta_presupuestada"], errors="coerce"
        )

        df_vs_presup, resumen_presup = calcular_ventas_vs_presupuesto(
            combinado[["fecha", "region", "producto", "ventas"]].copy(),
            presupuesto[["fecha", "venta_presupuestada"]].copy()
        )

        df_vs_presup.to_csv(OUT_VS_PRESUP, index=False)
        logger.info(f"✅ ventas_vs_presupuesto.csv generado en {OUT_VS_PRESUP}")

        if resumen_presup:
            resumen_presup_df = pd.DataFrame([resumen_presup])
            resumen_presup_df.to_csv(OUT_RESUMEN_PRESUP, index=False)
            logger.info(f"✅ resumen_presupuesto.csv generado en {OUT_RESUMEN_PRESUP}")

            logger.info(
                "📊 Presupuesto | "
                f"Desvío promedio: {resumen_presup['desvio_promedio']:.2f} | "
                f"% días sobre presupuesto: {resumen_presup['pct_dias_sobre_presupuesto']:.2f}% | "
                f"Mejor día: {resumen_presup['mejor_dia_fecha']} ({resumen_presup['mejor_dia_desvio']:.2f}) | "
                f"Peor día: {resumen_presup['peor_dia_fecha']} ({resumen_presup['peor_dia_desvio']:.2f})"
            )
        else:
            logger.warning("⚠️ No se pudo generar resumen de presupuesto por falta de datos válidos.")

    # 10) generar gráficas + insights
    insights, chart_paths = generar_graficas_y_insights(
        historico_path=HIST_PATH,
        output_dir="output/charts"
    )
    logger.info("✅ Gráficas e insights generados")

    # 11) generar reporte HTML
    try:
        generar_reporte_html(insights, chart_paths)
        logger.info("✅ Reporte HTML generado correctamente")
    except Exception as e:
        logger.error(f"❌ Error generando HTML: {e}")

    # 12) exportar KPIs adicionales
    res["por_producto"].to_csv(OUT_CSV)

    with pd.ExcelWriter(OUT_XLSX) as writer:
        res["por_producto"].to_excel(writer, sheet_name="KPI_Producto", index=True)
        res["por_region"].to_excel(writer, sheet_name="KPI_Region", index=True)
        res["pct_sobre_prod"].to_frame("pct").to_excel(writer, sheet_name="Pct_Sobre_Prom_Prod", index=True)
        res["pct_sobre_reg"].to_frame("pct").to_excel(writer, sheet_name="Pct_Sobre_Prom_Region", index=True)

    # 13) fin del pipeline
    logger.info("✅ Pipeline OK: histórico actualizado y reportes generados en output/")


if __name__ == "__main__":
    logger = get_logger("update_pipeline", "logs/pipeline.log")
    try:
        main()
    except Exception:
        logger.exception("❌ Error en el pipeline (update_pipeline.py)")
        raise