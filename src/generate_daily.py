import os
import pandas as pd
import numpy as np

def generar_datos_dia(fecha, n=200, seed=None):
    """
    Genera un DataFrame simulando ventas para una fecha.
    n = cantidad de registros del día
    """
    if seed is not None:
        np.random.seed(seed)

    regiones = ["Norte", "Sur", "Centro"]
    productos = ["A", "B", "C"]

    df = pd.DataFrame({
        "fecha": [pd.to_datetime(fecha).date()] * n,
        "region": np.random.choice(regiones, n),
        "producto": np.random.choice(productos, n),
        "ventas": np.random.randint(500, 2000, n)
    })
    return df

def guardar_csv_diario(df, carpeta="data/raw"):
    """
    Guarda el DF como CSV diario: ventas_YYYY-MM-DD.csv dentro de data/raw.
    Devuelve la ruta del archivo creado.
    """
    os.makedirs(carpeta, exist_ok=True)
    fecha = pd.to_datetime(df["fecha"].iloc[0]).date()
    nombre = f"ventas_{fecha}.csv"
    ruta = os.path.join(carpeta, nombre)
    df.to_csv(ruta, index=False)
    return ruta
