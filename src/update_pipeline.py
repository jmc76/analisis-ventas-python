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

RAW_DIR = "data/raw"
HIST_PATH = "data/processed/ventas_historico.csv"
OUT_XLSX = "output/kpi_daily.xlsx"
OUT_CSV = "output/kpi_daily.csv"


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


def main():
    logger = get_logger("update_pipeline", "logs/pipeline.log")
    os.makedirs("output", exist_ok=True)

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

    # 5) calcular KPI
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
    modelo.to_csv("output/modelo_dashboard.csv", index=False)
    logger.info("✅ modelo_dashboard.csv actualizado para Power BI")
    logger.debug(f"Keys disponibles en res: {list(res.keys())}")

    # 9) generar gráficas + insights
    insights, chart_paths = generar_graficas_y_insights(
        historico_path=HIST_PATH,
        output_dir="output/charts"
    )
    logger.info("✅ Gráficas e insights generados")

    # 10) generar reporte HTML
    try:
        generar_reporte_html(insights, chart_paths)
        logger.info("✅ Reporte HTML generado correctamente")
    except Exception as e:
        logger.error(f"❌ Error generando HTML: {e}")

    # 11) exportar KPIs adicionales
    res["por_producto"].to_csv(OUT_CSV)

    with pd.ExcelWriter(OUT_XLSX) as writer:
        res["por_producto"].to_excel(writer, sheet_name="KPI_Producto")
        res["por_region"].to_excel(writer, sheet_name="KPI_Region")
        res["pct_sobre_prod"].to_frame("pct").to_excel(writer, sheet_name="Pct_Sobre_Prom_Prod")
        res["pct_sobre_reg"].to_frame("pct").to_excel(writer, sheet_name="Pct_Sobre_Prom_Region")

    # 12) fin del pipeline
    logger.info("✅ Pipeline OK: histórico actualizado y reportes generados en output/")


if __name__ == "__main__":
    logger = get_logger("update_pipeline", "logs/pipeline.log")
    try:
        main()
    except Exception:
        logger.exception("❌ Error en el pipeline (update_pipeline.py)")
        raise