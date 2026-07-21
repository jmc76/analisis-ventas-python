import pandas as pd
import numpy as np

from datetime import datetime

HIST_PATH = "data/processed/ventas_historico.csv"

OUT_PATH = "data/processed/ventas_historico_finanzas.csv"

FIN_PATH = "data/processed/ventas_historico_finanzas.csv"

OUT_COBRANZAS = "output/cobranzas_proyectadas.csv"

OUT_RESUMEN = "output/resumen_financiero.csv"

OUT_AGING = "output/aging_cuentas_por_cobrar.csv"

def cargar_historico():

    df = pd.read_csv(HIST_PATH)

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

    return df

def asignar_condicion_pago(df):

    condiciones = np.select(

        [
            df.index % 100 < 40,
            df.index % 100 < 75,
            df.index % 100 < 95
        ],

        [
            "CONTADO",
            "30D",
            "60D"
        ],

        default="90D"
    )

    df["condicion_pago"] = condiciones

    return df

def agregar_fecha_cobro(df):

    dias = {

        "CONTADO": 0,
        "30D": 30,
        "60D": 60,
        "90D": 90
    }

    df["fecha_cobro"] = (

        df["fecha"]

        +

        pd.to_timedelta(
            df["condicion_pago"].map(dias),
            unit="D"
        )

    )

    return df

def generar_finanzas():

    df = cargar_historico()

    df = asignar_condicion_pago(df)

    df = agregar_fecha_cobro(df)

    df = agregar_estado_cobro(df)

    df.to_csv(
        OUT_PATH,
        index=False
    )

    cobranzas = generar_cobranzas_proyectadas(df)

    cobranzas.to_csv(
        OUT_COBRANZAS,
        index=False
    )

    resumen = generar_resumen_financiero(df)

    resumen.to_csv(
        OUT_RESUMEN,
        index=False
    )

    aging = generar_aging_cuentas_por_cobrar(df)

    aging.to_csv(
        OUT_AGING,
        index=False
    )

    print(
        "✅ ventas_historico_finanzas.csv generado"
    )

    print(
        "✅ cobranzas_proyectadas.csv generado"
    )

    print(
        "✅ resumen_financiero.csv generado"
    )

def agregar_estado_cobro(df):

    hoy = pd.Timestamp.today().normalize()

    riesgo = {
        "CONTADO": 0,
        "30D": 2,
        "60D": 5,
        "90D": 10
    }

    estados = []
    cobrados = []
    incobrables = []

    for idx, row in df.iterrows():

        if row["fecha_cobro"] > hoy:

            estados.append("PENDIENTE")
            cobrados.append(0)
            incobrables.append(0)

        else:

            prob = riesgo[row["condicion_pago"]]

            score = (
                idx
                + int(row["ventas"])
            ) % 100

            if score < prob:

                estados.append("INCOBRABLE")
                cobrados.append(0)
                incobrables.append(row["ventas"])

            else:

                estados.append("COBRADA")
                cobrados.append(row["ventas"])
                incobrables.append(0)

    df["estado_cobro"] = estados
    df["importe_cobrado"] = cobrados
    df["importe_incobrable"] = incobrables

    return df

def generar_cobranzas_proyectadas(df):

    cobranzas = (

        df.groupby("fecha_cobro", as_index=False)

        .agg(
            importe_esperado=(
                "ventas",
                "sum"
            ),

            importe_cobrado=(
                "importe_cobrado",
                "sum"
            ),

            importe_incobrable=(
                "importe_incobrable",
                "sum"
            )
        )

    )

    return cobranzas

def generar_resumen_financiero(df):

    facturado = float(df["ventas"].sum())

    cobrado = float(df["importe_cobrado"].sum())

    incobrable = float(df["importe_incobrable"].sum())

    pendiente = float(
        df.loc[
            df["estado_cobro"] == "PENDIENTE",
            "ventas"
        ].sum()
    )

    cuentas_por_cobrar = pendiente

    pct_recuperacion = (

        cobrado / facturado * 100

        if facturado > 0

        else 0

    )

    pct_incobrabilidad = (

        incobrable / facturado * 100

        if facturado > 0

        else 0

    )

    cash_conversion_rate = (

        cobrado / facturado * 100

        if facturado > 0

        else 0

    )

    # ==========================
    # DSO (Days Sales Outstanding)
    # ==========================

    df_dso = df.copy()

    df_dso["dias_cobro"] = (
        df_dso["fecha_cobro"]
        - df_dso["fecha"]
    ).dt.days

    dso = (
        (
            df_dso["ventas"]
            * df_dso["dias_cobro"]
        ).sum()
        /
        df_dso["ventas"].sum()
    )

    resumen = pd.DataFrame([{

        "facturado_total": facturado,

        "cobrado_total": cobrado,

        "pendiente_cobro": pendiente,

        "cuentas_por_cobrar": cuentas_por_cobrar,

        "incobrable_total": incobrable,

        "pct_recuperacion": pct_recuperacion,

        "cash_conversion_rate": cash_conversion_rate,

        "pct_incobrabilidad": pct_incobrabilidad,

        "dso": round(dso, 2)

    }])

    return resumen

def generar_aging_cuentas_por_cobrar(df):

    hoy = pd.Timestamp.today().normalize()

    pendientes = df[
        df["estado_cobro"] == "PENDIENTE"
    ].copy()

    pendientes["dias_pendientes"] = (
        hoy - pendientes["fecha"]
    ).dt.days

    pendientes["aging_bucket"] = pd.cut(

        pendientes["dias_pendientes"],

        bins=[
            -1,
            30,
            60,
            90,
            float("inf")
        ],

        labels=[
            "0-30",
            "31-60",
            "61-90",
            "+90"
        ]
    )

    aging = (
        pendientes
        .groupby(
            "aging_bucket",
            observed=False
        )["ventas"]
        .sum()
        .reset_index()
    )

    aging.columns = [
        "rango_dias",
        "cuentas_por_cobrar"
    ]

    return aging

if __name__ == "__main__":
    generar_finanzas()