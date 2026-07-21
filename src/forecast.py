import pandas as pd

from caja import SALDO_INICIAL

CAJA_PATH = "output/caja_proyectada.csv"

OUT_PATH = "output/forecast_caja.csv"

def cargar_caja():

    caja = pd.read_csv(
        CAJA_PATH
    )

    return caja

def generar_forecast():

    caja = cargar_caja()

    gastos = pd.read_csv(
        "data/processed/gastos_historico.csv"
    )

    variables = [
        "Comisiones",
        "IVA",
        "Ingresos Brutos"
    ]

    escenarios = {

        "Pesimista": 0.90,

        "Base": 1.00,

        "Optimista": 1.10

    }

    resultados = []

    for nombre, factor in escenarios.items():

        gastos_escenario = gastos.copy()

        gastos_escenario.loc[
            gastos_escenario["categoria"].isin(
                variables
            ),
            "importe"
        ] *= factor

        pagos_escenario = (
            gastos_escenario["importe"]
            .sum()
        )

        cobros_escenario = (
            caja["cobros"]
            .sum()
            * factor
        )

        saldo_final = (

            SALDO_INICIAL

            +

            cobros_escenario

            -

            pagos_escenario

        )

        resultados.append({

            "escenario": nombre,

            "factor_ventas": factor,

            "saldo_final_caja": round(
                saldo_final,
                2
            )

        })

    forecast = pd.DataFrame(
        resultados
    )

    forecast.to_csv(
        OUT_PATH,
        index=False
    )

    print(
        "✅ forecast_caja.csv generado"
    )

if __name__ == "__main__":

    generar_forecast()

