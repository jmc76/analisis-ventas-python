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

    columnas_importe = [
        "importe_esperado",
        "cobros",
        "importe_incobrable",
        "pagos",
        "flujo_neto",
        "saldo_caja"
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

    # ========================
    # KPIs de Tesorería
    # ========================

    caja_actual = float(
        flujo["saldo_caja"].iloc[-1]
    )

    burn_rate = abs(

        flujo.loc[
            flujo["flujo_neto"] < 0,
            "flujo_neto"
        ].mean()

    )

    if caja_actual <= 0:

        cash_runway = 0

    else:

        cash_runway = (

            caja_actual
            / burn_rate

            if burn_rate > 0

            else 0

        )

    kpis = pd.DataFrame([{

        "caja_actual": round(
            caja_actual,
            2
        ),

        "burn_rate": round(
            burn_rate,
            2
        ),

        "cash_runway": round(
            cash_runway,
            2
        )

    }])

    kpis.to_csv(
        "output/kpis_tesoreria.csv",
        index=False
    )


    print(
        "✅ caja_proyectada.csv generado"
    )

    print(
        f"💰 Caja Actual: {caja_actual:,.2f}"
    )

    print(
        f"🔥 Burn Rate: {burn_rate:,.2f}"
    )

    print(
        f"🚀 Cash Runway: {cash_runway:.2f} días"
    )

if __name__ == "__main__":

    generar_caja()