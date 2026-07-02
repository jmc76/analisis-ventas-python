import pandas as pd

def generar_presupuesto():

    # Cargar histórico real
    df = pd.read_csv("data/processed/ventas_historico.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Ventas reales por día
    ventas_diarias = df.groupby("fecha", as_index=False)["ventas"].sum()
    ventas_diarias = ventas_diarias.rename(columns={"ventas": "ventas_reales"})

    # Promedio móvil de 7 días (sin usar el mismo día)
    ventas_diarias["venta_presupuestada"] = (
        ventas_diarias["ventas_reales"]
        .shift(1)
        .rolling(window=7, min_periods=3)
        .mean()
    )

    # Rellenar valores iniciales con promedio general
    promedio_general = ventas_diarias["ventas_reales"].mean()
    ventas_diarias["venta_presupuestada"] = ventas_diarias["venta_presupuestada"].fillna(promedio_general)

    # Redondear valores
    ventas_diarias["venta_presupuestada"] = ventas_diarias["venta_presupuestada"].round(0)

    # Dejar columnas finales
    df_final = ventas_diarias[["fecha", "venta_presupuestada"]]

    # Guardar CSV
    df_final.to_csv("data/processed/presupuesto_ventas.csv", index=False)

    print("✅ Presupuesto generado con promedio móvil de 7 días")

if __name__ == "__main__":
    generar_presupuesto()