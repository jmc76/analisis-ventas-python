import pandas as pd

HIST_PATH = "data/processed/ventas_historico.csv"

OUT_PATH = "data/processed/gastos_historico.csv"


def cargar_ventas_diarias():

    df = pd.read_csv(HIST_PATH)

    df["fecha"] = pd.to_datetime(
        df["fecha"]
    )

    ventas_dia = (
        df.groupby("fecha", as_index=False)
        .agg(
            ventas=(
                "ventas",
                "sum"
            )
        )
    )

    return ventas_dia


def generar_gastos():

    ventas_dia = cargar_ventas_diarias()

    registros = []

    ultimo_mes = None

    for _, row in ventas_dia.iterrows():

        fecha = row["fecha"]

        ventas = row["ventas"]

        iva = ventas * 0.21

        iibb = ventas * 0.035

        tasa_municipal = 15000

        # Gastos fijos: una sola vez por mes
        if fecha.month != ultimo_mes:

            registros.extend([

                [fecha, "FIJO", "Sueldos", 850000],

                [fecha, "FIJO", "Alquiler", 120000],

                [fecha, "FIJO", "Internet", 15000],

                [fecha, "FIJO", "Software", 25000],

                [fecha, "FIJO", "Servicios", 30000]

            ])

            ultimo_mes = fecha.month

        # Gastos variables e impuestos: diarios
        registros.extend([

            [fecha, "VARIABLE", "Marketing", 45000],

            [fecha, "VARIABLE", "Logistica", 35000],

            [fecha, "VARIABLE", "Comisiones", 25000],

            [fecha, "VARIABLE", "Packaging", 12000],

            [fecha, "IMPUESTO", "IVA", round(iva, 2)],

            [fecha, "IMPUESTO", "Ingresos Brutos", round(iibb, 2)],

            [fecha, "IMPUESTO", "Tasa Municipal", tasa_municipal]

        ])

    gastos = pd.DataFrame(

        registros,

        columns=[
            "fecha",
            "tipo",
            "categoria",
            "importe"
        ]
    )

    gastos.to_csv(
        OUT_PATH,
        index=False
    )

    print(
        "✅ gastos_historico.csv generado"
    )


if __name__ == "__main__":

    generar_gastos()