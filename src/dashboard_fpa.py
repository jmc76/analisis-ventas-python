import json

import pandas as pd

from datetime import datetime

RESUMEN_PATH = "output/resumen_financiero.csv"

AGING_PATH = "output/aging_cuentas_por_cobrar.csv"

TESORERIA_PATH = "output/kpis_tesoreria.csv"

FORECAST_PATH = "output/forecast_caja.csv"

PNL_PATH = "output/estado_resultados.csv"

CAJA_PATH = "output/caja_proyectada.csv"

OUT_PATH = "output/dashboard_fpa.html"

FINANCIAMIENTO_PATH = (
    "output/escenarios_financiamiento.csv"
)


def generar_dashboard():

    resumen = pd.read_csv(
        RESUMEN_PATH
    )

    aging = pd.read_csv(
        AGING_PATH
    )

    tesoreria = pd.read_csv(
        TESORERIA_PATH
    )

    forecast = pd.read_csv(
        FORECAST_PATH
    )

    financiamiento = pd.read_csv(
        FINANCIAMIENTO_PATH
    )

    minimo = financiamiento.loc[
        financiamiento["escenario"]
        == "Mínimo Técnico"
    ].iloc[0]

    operativo = financiamiento.loc[
        financiamiento["escenario"]
        == "Operativo (30 días)"
    ].iloc[0]

    pnl = pd.read_csv(
        PNL_PATH
    )

    caja = pd.read_csv(
        CAJA_PATH
    )

    r = resumen.iloc[0]

    t = tesoreria.iloc[0]

    p = pnl.iloc[0]

    # =========================
    # Aging
    # =========================

    aging_html = aging.copy()

    aging_html["cuentas_por_cobrar"] = (
        aging_html["cuentas_por_cobrar"]
        .map(lambda x: f"${x:,.0f}")
    )

    aging_html.columns = [
        col.replace("_", " ")
        for col in aging_html.columns
    ]

    # =========================
    # Forecast
    # =========================

    forecast_html = forecast.copy()

    forecast_html["saldo_final_caja"] = (
        forecast_html["saldo_final_caja"]
        .map(lambda x: f"${x:,.0f}")
    )

    forecast_html.columns = [
        col.replace("_", " ")
        for col in forecast_html.columns
    ]

    # =========================
    # P&L
    # =========================

    pnl_html = pnl.copy()

    columnas_monetarias = [

        "ventas",

        "gastos_variables",

        "margen_contribucion",

        "gastos_fijos",

        "ebitda",

        "impuestos",

        "resultado_neto"

    ]

    for col in columnas_monetarias:

        if col in pnl_html.columns:

            pnl_html[col] = (
                pnl_html[col]
                .map(lambda x: f"${x:,.0f}")
            )

    # Recién ahora cambiamos los títulos

    columnas_porcentaje = [

        "margen_contribucion_pct",

        "ebitda_pct",

        "margen_neto_pct"

    ]

    for col in columnas_porcentaje:

        if col in pnl_html.columns:

            pnl_html[col] = (
                pnl_html[col]
                .map(lambda x: f"{x:.2f}%")
            )

    pnl_html.columns = [
        col.replace("_", " ")
        for col in pnl_html.columns
    ]

    caja_class = (
        "negative"
        if t["caja_actual"] < 0
        else "positive"
    )

    runway_class = (
        "negative"
        if t["cash_runway"] == 0
        else "positive"
    )

    ebitda_class = (
        "positive"
        if p["ebitda"] > 0
        else "negative"
    )

    margen_neto_class = (
        "positive"
        if p["resultado_neto"] > 0
        else "negative"
    )

    margen_contribucion_class = (
        "positive"
        if p["margen_contribucion"] > 0
        else "negative"
    )

    if t["burn_rate"] < 50000:

        burn_class = "positive"

    elif t["burn_rate"] < 100000:

        burn_class = "warning"

    else:

        burn_class = "negative"

    fechas_caja = (
        caja["fecha"]
        .tolist()
    )

    saldos_caja = (
        caja["saldo_caja"]
        .tolist()
    )

    import json

    fechas_caja_js = json.dumps(
        fechas_caja
    )

    saldos_caja_js = json.dumps(
        saldos_caja
    )

    financiamiento_html = (
        financiamiento.copy()
    )

    financiamiento_html["prestamo"] = (
        financiamiento_html["prestamo"]
        .map(lambda x: f"${x:,.0f}")
    )

    financiamiento_html["saldo_final"] = (
        financiamiento_html["saldo_final"]
        .map(lambda x: f"${x:,.0f}")
)

    minimo = financiamiento.loc[
        financiamiento["escenario"]
        == "Mínimo Técnico"
    ].iloc[0]

    operativo = financiamiento.loc[
        financiamiento["escenario"]
        == "Operativo (30 días)"
    ].iloc[0]

    insights = [

        "⚠ Caja proyectada final negativa.",

        "⚠ Cash Runway agotado.",

        "✅ EBITDA positivo.",

        "✅ Bad Debt inferior al 1%.",

        "⚠ Escenario optimista continúa con caja negativa.",

        f"✅ El financiamiento mínimo para evitar el quiebre de caja es de "
        f"${minimo['prestamo']:,.0f}.",

        f"✅ Para cubrir además 30 días de gastos fijos se requieren "
        f"${operativo['prestamo']:,.0f}."

    ]

    insights_html = ""

    for insight in insights:

        insights_html += f"<li>{insight}</li>"

    html = f"""

    <html>

    <head>

    <title>FP&A Dashboard</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>

    body {{
        font-family: Arial;
        margin: 30px;
        background-color: #f5f7fa;
    }}

    h1 {{
        color: #1f4e79;
    }}

    h2 {{
        color: #17406a;
        border-bottom: 2px solid #ddd;
        padding-bottom: 5px;
    }}

    .cards {{
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 20px;
    }}

    .card {{
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        width: 220px;
    }}

    .card-title {{
        font-size: 12px;
        color: grey;
    }}

    .card-value {{
        font-size: 24px;
        font-weight: bold;
    }}

    .positive {{
        color: #2ca02c;
    }}

    .negative {{
        color: #d62728;
    }}

    .warning {{
        color: #ff7f0e;
    }}

    .revenue {{
        border-left: 6px solid #1f77b4;
    }}

    .ar {{
        border-left: 6px solid #ff7f0e;
    }}

    .cash {{
        border-left: 6px solid #2ca02c;
    }}

    .profit {{
        border-left: 6px solid #9467bd;
    }}

    .forecast {{
        border-left: 6px solid #d62728;
    }}

    table {{
        border-collapse: collapse;
        width: auto;
        min-width: 450px;
        background: white;
    }}

    .table-container {{
        display: inline-block;
        margin-bottom: 30px;
    }}

    th, td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }}

    th {{
        background-color: #1f4e79;
        color: white;
    }}

    ul {{
        background: white;
        padding: 20px;
        border-radius: 10px;
    }}

    </style>

    </head>

    <body>

    <h1>Financial Planning & Analysis Dashboard</h1>

    <p>
        Actualizado:
        {datetime.now().strftime("%Y-%m-%d %H:%M")}
    </p>

    <h2>Revenue</h2>

    <div class="cards">

        <div class="card revenue">
            <div class="card-title">Facturado</div>
            <div class="card-value">${r['facturado_total']:,.0f}</div>
        </div>

        <div class="card revenue">
            <div class="card-title">Cobrado</div>
            <div class="card-value">${r['cobrado_total']:,.0f}</div>
        </div>

        <div class="card revenue">
            <div class="card-title">Recovery Rate</div>
            <div class="card-value">{r['pct_recuperacion']:.2f}%</div>
        </div>

        <div class="card revenue">
            <div class="card-title">Cash Conversion</div>
            <div class="card-value">{r['cash_conversion_rate']:.2f}%</div>
        </div>

        <div class="card revenue">
            <div class="card-title">Bad Debt %</div>
            <div class="card-value">{r['pct_incobrabilidad']:.2f}%</div>
        </div>

    </div>

    <h2>Accounts Receivable</h2>

    <div class="cards">

        <div class="card ar">
            <div class="card-title">Accounts Receivable</div>
            <div class="card-value">${r['cuentas_por_cobrar']:,.0f}</div>
        </div>

        <div class="card ar">
            <div class="card-title">DSO</div>
            <div class="card-value">{r['dso']:.2f}</div>
        </div>

        <div class="card ar">
            <div class="card-title">Incobrables</div>
            <div class="card-value">${r['incobrable_total']:,.0f}</div>
        </div>

    </div>

    <div class="table-container">
        {aging_html.to_html(index=False)}
    </div>

    <h2>Cash Management</h2>

    <div class="cards">

        <div class="card cash">
            <div class="card-title">Caja Actual</div>
            <div class="card-value {caja_class}">
                ${t['caja_actual']:,.0f}
            </div>
        </div>

        <div class="card cash">
            <div class="card-title">Burn Rate</div>
            <div class="card-value {burn_class}">
                ${t['burn_rate']:,.0f}
            </div>
        </div>

        <div class="card cash">
            <div class="card-title">Cash Runway</div>
            <div class="card-value {runway_class}">
                {t['cash_runway']:.0f} días
            </div>
        </div>    

        </div>

        <div
            style="
                background:white;
                padding:20px;
                border-radius:10px;
                margin-top:20px;
                margin-bottom:30px;
                width:100%;
                box-sizing:border-box;
            "
        >

            <h3>Evolución de Caja Proyectada</h3>

            <div
                style="
                    height:400px;
                    width:100%;
                "
            >
                <canvas id="cashChart"></canvas>
            </div>
        </div>

    </div>

    <h2>Profitability</h2>

    <div class="cards">

        <div class="card profit">
            <div class="card-title">
                Margen Contribución
            </div>
            <div class="card-value {margen_contribucion_class}">
                {p['margen_contribucion_pct']:.2f}%
            </div>
        </div>
   
        <div class="card profit">
            <div class="card-title">
                EBITDA %
            </div>
            <div class="card-value {ebitda_class}">
                {p['ebitda_pct']:.2f}%
            </div>
        </div>

        <div class="card profit">
            <div class="card-title">
                Margen Neto
            </div>
            <div class="card-value {margen_neto_class}">
                {p['margen_neto_pct']:.2f}%
            </div>
        </div>

</div>

<div class="table-container">
    {pnl_html.to_html(index=False)}
</div>

    <h2>Forecast & Scenarios</h2>

    <div class="table-container">
        {forecast_html.to_html(index=False)}
    </div>

    <h2>Funding Scenarios</h2>

    <div class="table-container">
        {financiamiento_html.to_html(index=False)}
    </div>

    <h2>Financial Insights</h2>

    <ul>

        {insights_html}

    </ul>

    <script>

    const cashCtx =
    document.getElementById(
        "cashChart"
    );

    new Chart(
        cashCtx,
        {{

            type: "line",

            data: {{

                labels:
                {fechas_caja_js},

                datasets: [{{
                    label:
                    "Saldo Caja",

                    data:
                    {saldos_caja_js},

                    borderColor:
                    "#2ca02c",

                    backgroundColor:
                    "rgba(44,160,44,0.15)",

                    fill: true,

                    tension: 0.3

                }}]

            }},

            options: {{

                responsive: true,

                maintainAspectRatio: false,

                scales: {{

                    x: {{

                        ticks: {{

                            maxTicksLimit: 10

                        }}

                    }},

                    y: {{

                        ticks: {{

                            callback: function(value) {{
                                return '$' + value.toLocaleString();
                            }}

                        }}

                    }}

                }},

                plugins: {{

                    legend: {{

                        display: true

                    }}

                }}

            }}

        }}
    );

    </script>

    </body>

    </html>

    """

    with open(
        OUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print(
        "✅ dashboard_fpa.html generado"
    )


if __name__ == "__main__":

    generar_dashboard()
