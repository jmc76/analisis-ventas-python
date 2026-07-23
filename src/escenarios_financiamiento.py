import pandas as pd

FORECAST_PATH = "output/forecast_caja.csv"

OUT_PATH = "output/escenarios_financiamiento.csv"


def generar_escenarios_financiamiento():

    forecast = pd.read_csv(
        FORECAST_PATH
    )

    saldo_base = float(
        forecast.loc[
            forecast["escenario"] == "Base",
            "saldo_final_caja"
        ].iloc[0]
    )

    gastos = pd.read_csv(
        "data/processed/gastos_historico.csv"
    )

    # Gastos variables ya considerados en forecast

    variables = [

        "Comisiones",

        "IVA",

        "Ingresos Brutos"

    ]

    gastos_fijos = gastos[
        ~gastos["categoria"].isin(
            variables
        )
    ].copy()

    gastos_fijos["fecha"] = pd.to_datetime(
        gastos_fijos["fecha"]
    )

    meses = (
        gastos_fijos["fecha"]
        .dt.to_period("M")
        .nunique()
    )

    gasto_fijo_mensual = (
        gastos_fijos["importe"].sum()
        / meses
    )

    print(
        f"Gasto fijo mensual: {gasto_fijo_mensual:,.2f}"
    )

    prestamo_minimo = abs(
        min(
            saldo_base,
            0
        )
    )

    prestamo_operativo = (
        prestamo_minimo
        + gasto_fijo_mensual
    )

    prestamo_conservador = (
        prestamo_minimo
        + (2 * gasto_fijo_mensual)
    )

    resultados = [

        {

            "escenario":
            "Base",

            "prestamo":
            0,

            "saldo_final":
            saldo_base

        },

        {

            "escenario":
            "Mínimo Técnico",

            "prestamo":
            round(
                prestamo_minimo,
                2
            ),

            "saldo_final":
            0

        },

        {

            "escenario":
            "Operativo (30 días)",

            "prestamo":
            round(
                prestamo_operativo,
                2
            ),

            "saldo_final":
            round(
                gasto_fijo_mensual,
                2
            )

        },

        {

            "escenario":
            "Conservador (60 días)",

            "prestamo":
            round(
                prestamo_conservador,
                2
            ),

            "saldo_final":
            round(
                2 * gasto_fijo_mensual,
                2
            )

        }

]
    
    df = pd.DataFrame(
        resultados
    )

    df.to_csv(
        OUT_PATH,
        index=False
    )

    print(
        "✅ escenarios_financiamiento.csv generado"
    )


if __name__ == "__main__":

    generar_escenarios_financiamiento()