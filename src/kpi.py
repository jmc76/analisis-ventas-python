"""
kpi.py
------

Funciones de KPI (Key Performance Indicators) para el proyecto.

Objetivo:
- Enriquecer el dataset con métricas comparativas (promedios) y banderas (flags)
  como "venta por encima del promedio".
- Generar tablas de resumen listas para exportar a Excel/CSV.

Este módulo se usa desde update_pipeline.py.
"""

import pandas as pd


def agregar_kpis_vs_promedio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas KPI al DataFrame comparando cada venta vs promedios.

    Requiere que df tenga al menos estas columnas:
    - fecha
    - region
    - producto
    - ventas

    Devuelve una COPIA del DataFrame con columnas adicionales:
    - promedio_producto
    - venta_sobre_prom_producto (True/False)
    - promedio_region
    - venta_sobre_prom_region (True/False)

    Nota:
    - Si 'fecha' viene como string, se convierte a datetime.
    - Las comparaciones contra promedios te permiten detectar performance "mejor a lo normal".
    """

    # Trabajamos sobre una copia para no modificar el df original accidentalmente
    df = df.copy()

    # Aseguramos que fecha sea datetime (buena práctica para análisis por tiempo)
    df["fecha"] = pd.to_datetime(df["fecha"])

    # -----------------------------
    # KPI 1: Promedio por PRODUCTO
    # -----------------------------
    # Calcula el promedio de ventas por producto (A/B/C...)
    prom_prod = df.groupby("producto")["ventas"].mean()

    # Mapea ese promedio a cada fila según su producto
    df["promedio_producto"] = df["producto"].map(prom_prod)

    # Flag: True si la venta de la fila está por encima del promedio del producto
    df["venta_sobre_prom_producto"] = df["ventas"] > df["promedio_producto"]

    # ---------------------------
    # KPI 2: Promedio por REGIÓN
    # ---------------------------
    prom_reg = df.groupby("region")["ventas"].mean()
    df["promedio_region"] = df["region"].map(prom_reg)
    df["venta_sobre_prom_region"] = df["ventas"] > df["promedio_region"]

    return df


def resumen_kpis(df: pd.DataFrame) -> dict:
    """
    Genera tablas de resumen (listas para exportar).

    IMPORTANTE:
    - Esta función asume que el df YA contiene las columnas:
      'venta_sobre_prom_producto' y 'venta_sobre_prom_region'.
    - Es decir: primero deberías haber corrido agregar_kpis_vs_promedio(df).

    Devuelve un diccionario con estas claves:
    - "por_producto": tabla con count/sum/mean de ventas por producto
    - "por_region": tabla con count/sum/mean de ventas por región
    - "pct_sobre_prod": serie con % de ventas sobre el promedio por producto
    - "pct_sobre_reg": serie con % de ventas sobre el promedio por región

    Nota:
    - Los porcentajes salen entre 0 y 1 (ej: 0.52 = 52%).
    """

    # Validación “empresa”: si faltan columnas KPI, damos un error claro
    columnas_kpi = {"venta_sobre_prom_producto", "venta_sobre_prom_region"}
    faltantes = columnas_kpi - set(df.columns)
    if faltantes:
        raise ValueError(
            f"Faltan columnas KPI {faltantes}. "
            "Ejecuta primero agregar_kpis_vs_promedio(df) antes de resumen_kpis(df)."
        )

    # Aseguramos que fecha esté en formato datetime (no es estrictamente necesario aquí, pero es buena práctica)
    if "fecha" in df.columns:
        df = df.copy()
        df["fecha"] = pd.to_datetime(df["fecha"])

    # --------------------------
    # Resumen 1: KPI por producto
    # --------------------------
    por_producto = (
        df.groupby("producto")["ventas"]
          .agg(["count", "sum", "mean"])
          .sort_values("sum", ascending=False)
    )

    # ------------------------
    # Resumen 2: KPI por región
    # ------------------------
    por_region = (
        df.groupby("region")["ventas"]
          .agg(["count", "sum", "mean"])
          .sort_values("sum", ascending=False)
    )

    # -------------------------------------------------------
    # Resumen 3: % de ventas sobre el promedio (por producto)
    # -------------------------------------------------------
    # Como la columna es booleana (True/False), mean() da el porcentaje:
    # True=1, False=0 → promedio = proporción de True
    pct_sobre_prom_prod = (
        df.groupby("producto")["venta_sobre_prom_producto"]
          .mean()
          .sort_values(ascending=False)
    )

    # -----------------------------------------------------
    # Resumen 4: % de ventas sobre el promedio (por región)
    # -----------------------------------------------------
    pct_sobre_prom_region = (
        df.groupby("region")["venta_sobre_prom_region"]
          .mean()
          .sort_values(ascending=False)
    )

    # ✅ Claves consistentes con update_pipeline.py
    return {
        "por_producto": por_producto,
        "por_region": por_region,
        # Estas claves son las que tu pipeline usa en el Excel:
        "pct_sobre_prod": pct_sobre_prom_prod,
        "pct_sobre_reg": pct_sobre_prom_region
    }
