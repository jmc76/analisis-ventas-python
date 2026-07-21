import pandas as pd

FLUJO_PATH = "output/flujo_caja.csv"

OUT_PATH = "output/caja_proyectada.csv"

SALDO_INICIAL = 5000000


def cargar_flujo():

    flujo = pd.read_csv(
        FLUJO_PATH
    )

    flujo["fecha"] = pd.to_datetime(
        flujo["fecha"]
    )

    return flujo


def generar_caja():

    flujo = cargar_flujo()

    flujo = flujo.sort_values(
        "fecha"
    )

    flujo["saldo_caja"] = (

        SALDO_INICIAL

        +

        flujo["flujo_neto"].cumsum()

    )

    # Redondear antes de exportar

    flujo["flujo_neto"] = (
        flujo["flujo_neto"]
        .round(2)
    )

    flujo["saldo_caja"] = (
        flujo["saldo_caja"]
        .round(2)
    )

    flujo.to_csv(
        OUT_PATH,
        index=False
    )

    print(
        "✅ caja_proyectada.csv generado"
    )


if __name__ == "__main__":

    generar_caja()