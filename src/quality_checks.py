"""
quality_checks.py
Validaciones de calidad de datos para el pipeline.
"""

import pandas as pd


def validar_no_vacio(df: pd.DataFrame, nombre: str = "DataFrame"):
    """Frena si el DataFrame está vacío."""
    if df is None or df.empty:
        raise ValueError(f"{nombre} está vacío. No hay datos para procesar.")


def validar_columnas(df: pd.DataFrame, columnas_esperadas, nombre: str = "DataFrame"):
    """Frena si faltan columnas obligatorias."""
    faltantes = set(columnas_esperadas) - set(df.columns)
    if faltantes:
        raise ValueError(f"{nombre}: faltan columnas obligatorias: {faltantes}")


def validar_tipos_y_nulos_basicos(df: pd.DataFrame, nombre: str = "DataFrame") -> pd.DataFrame:
    """
    - Convierte fecha a datetime (invalidas quedan NaT)
    - Convierte ventas a numérico (invalidas quedan NaN)
    - Frena si hay fechas/ventas inválidas
    """
    df = df.copy()

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["ventas"] = pd.to_numeric(df["ventas"], errors="coerce")

    if df["fecha"].isna().any():
        raise ValueError(f"{nombre}: hay fechas inválidas en la columna 'fecha'.")

    if df["ventas"].isna().any():
        raise ValueError(f"{nombre}: hay valores inválidos en la columna 'ventas' (no numéricos).")

    return df


def validar_rangos_ventas(df: pd.DataFrame, min_ok: float = 1, max_ok: float = 200000, nombre: str = "DataFrame"):
    """Frena si hay ventas fuera de un rango razonable."""
    fuera = df[(df["ventas"] < min_ok) | (df["ventas"] > max_ok)]
    if not fuera.empty:
        raise ValueError(
            f"{nombre}: hay ventas fuera de rango ({min_ok}..{max_ok}). "
            f"Ejemplos:\n{fuera.head(5)}"
        )


def warning_outliers_iqr(df: pd.DataFrame, nombre: str = "DataFrame"):
    """
    NO frena el pipeline.
    Solo imprime advertencia si hay outliers en 'ventas' usando IQR.
    """
    q1 = df["ventas"].quantile(0.25)
    q3 = df["ventas"].quantile(0.75)
    iqr = q3 - q1

    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr

    outliers = df[(df["ventas"] < lim_inf) | (df["ventas"] > lim_sup)]
    if not outliers.empty:
        print(f"⚠️ WARNING ({nombre}): {len(outliers)} outliers detectados por IQR.")
        print(outliers.sort_values("ventas", ascending=False).head(5))


def validar_duplicados(df: pd.DataFrame, subset=None, nombre: str = "DataFrame"):
    """Frena si detecta duplicados según un subset de columnas."""
    if subset is None:
        subset = ["fecha", "region", "producto", "ventas"]

    dup = df.duplicated(subset=subset).sum()
    if dup > 0:
        raise ValueError(f"{nombre}: se detectaron {dup} filas duplicadas según {subset}.")