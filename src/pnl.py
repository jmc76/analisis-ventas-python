import pandas as pd

VENTAS_PATH = "data/processed/ventas_historico.csv"

GASTOS_PATH = "data/processed/gastos_historico.csv"

OUT_PATH = "output/estado_resultados.csv"


def cargar_ventas():

    ventas = pd.read_csv(
        VENTAS_PATH
    )

    return ventas


def cargar_gastos():

    gastos = pd.read_csv(
        GASTOS_PATH
    )

    return gastos


def generar_estado_resultados():

    ventas = cargar_ventas()

    gastos = cargar_gastos()

    ingresos = float(
        ventas["ventas"].sum()
    )

    gastos_variables = float(

        gastos.loc[
            gastos["tipo"] == "VARIABLE",
            "importe"
        ].sum()

    )

    gastos_fijos = float(

        gastos.loc[
            gastos["tipo"] == "FIJO",
            "importe"
        ].sum()

    )

    impuestos = float(

        gastos.loc[
            gastos["tipo"] == "IMPUESTO",
            "importe"
        ].sum()

    )

    margen_contribucion = (
        ingresos
        - gastos_variables
    )

    margen_contribucion_pct = (

        margen_contribucion
        / ingresos
        * 100

        if ingresos > 0

        else 0

    )

    ebitda = (
        margen_contribucion
        - gastos_fijos
    )

    ebitda_pct = (

        ebitda
        / ingresos
        * 100

        if ingresos > 0

        else 0

    )

    resultado_neto = (
        ebitda
        - impuestos
    )

    margen_neto_pct = (

        resultado_neto
        / ingresos
        * 100

        if ingresos > 0

        else 0

    )

    estado = pd.DataFrame([{

        "ventas": round(
            ingresos,
            2
        ),

        "gastos_variables": round(
            gastos_variables,
            2
        ),

        "margen_contribucion": round(
            margen_contribucion,
            2
        ),

        "margen_contribucion_pct": round(
            margen_contribucion_pct,
            2
        ),

        "gastos_fijos": round(
            gastos_fijos,
            2
        ),

        "ebitda": round(
            ebitda,
            2
        ),

        "ebitda_pct": round(
            ebitda_pct,
            2
        ),

        "impuestos": round(
            impuestos,
            2
        ),

        "resultado_neto": round(
            resultado_neto,
            2
        ),

        "margen_neto_pct": round(
            margen_neto_pct,
            2
        )

    }])

    estado.to_csv(
        OUT_PATH,
        index=False
    )

    print(
        "✅ estado_resultados.csv generado"
    )


if __name__ == "__main__":

    generar_estado_resultados()