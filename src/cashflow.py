import pandas as pd

COBRANZAS_PATH = "output/cobranzas_proyectadas.csv"

GASTOS_PATH = "data/processed/gastos_historico.csv"

OUT_PATH = "output/flujo_caja.csv"


def cargar_cobranzas():

    cobranzas = pd.read_csv(
        COBRANZAS_PATH
    )

    cobranzas["fecha_cobro"] = pd.to_datetime(
        cobranzas["fecha_cobro"]
    )

    cobranzas = cobranzas.rename(
        columns={
            "fecha_cobro": "fecha",
            "importe_cobrado": "cobros"
        }
    )

    return cobranzas


def cargar_gastos():

    gastos = pd.read_csv(
        GASTOS_PATH
    )

    gastos["fecha"] = pd.to_datetime(
        gastos["fecha"]
    )

    gastos = (
        gastos.groupby(
            "fecha",
            as_index=False
        )
        .agg(
            pagos=(
                "importe",
                "sum"
            )
        )
    )

    return gastos


def generar_flujo_caja():

    cobranzas = cargar_cobranzas()

    gastos = cargar_gastos()

    flujo = pd.merge(

        cobranzas,

        gastos,

        on="fecha",

        how="outer"

    )

    flujo["cobros"] = (
        flujo["cobros"]
        .fillna(0)
    )

    flujo["pagos"] = (
        flujo["pagos"]
        .fillna(0)
    )

    flujo["flujo_neto"] = (
        flujo["cobros"]
        - flujo["pagos"]
    )

    flujo = flujo.sort_values(
        "fecha"
    )

    # Redondear columnas monetarias

    columnas_importe = [
        "importe_esperado",
        "cobros",
        "importe_incobrable",
        "pagos",
        "flujo_neto"
    ]

    for col in columnas_importe:

        if col in flujo.columns:

            flujo[col] = (
                flujo[col]
                .round(2)
            )

    flujo.to_csv(
        OUT_PATH,
        index=False
    )

    print(
        "✅ flujo_caja.csv generado"
    )


if __name__ == "__main__":

    generar_flujo_caja()