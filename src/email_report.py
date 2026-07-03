import os
from turtle import position

def generar_reporte_html(
    insights,
    chart_paths,
    resumen_presup=None,
    output_file="output/reporte.html"
):
    """
    Genera un dashboard HTML con insights y gráficos.
    """

    # ✅ función imágenes
    def img_tag(path):
        if not path:
            return ""
        filename = os.path.basename(path)
        return f'<img src="charts/{filename}" style="width:100%; border-radius:10px;">'

    # ✅ cálculo vs día anterior
    delta_html = ""

    try:
        ventas_ordenadas = sorted(
            zip(insights["serie_fechas"], insights["serie_ventas"]),
            key=lambda x: x[0]
        )

        if len(ventas_ordenadas) >= 2:
            _, v_ant = ventas_ordenadas[-2]
            _, v_ultimo = ventas_ordenadas[-1]

            diff = v_ultimo - v_ant
            pct = diff / v_ant if v_ant != 0 else 0

            color = "#16a34a" if diff >= 0 else "#dc2626"
            signo = "+" if diff >= 0 else ""

            delta_html = f"""
            <div class="kpi-sub" style="color:{color}; font-weight:bold;">
                {signo}{pct:.1%} vs día anterior
            </div>
            """

    except Exception:
        delta_html = ""

    # ✅ mejor performance
    best_perf_html = ""
    best_perf_card = ""
    presupuesto_card = ""

    if resumen_presup:

        presupuesto_card = f"""
        <div class="card">
            <div class="kpi-title">Cumplimiento presupuesto</div>
            <div class="kpi-value">
                {resumen_presup['pct_dias_sobre_presupuesto']:.1f}%
            </div>
            <div class="kpi-sub">
                Días sobre objetivo
            </div>
        </div>
        """
           

    if insights.get("best_perf_producto") is not None:
        best_perf_html = f"""
        <li><b>Mejor performance relativa:</b> {insights['best_perf_producto']} ({insights['best_perf_val']:.1%})</li>
        """

        best_perf_card = f"""
        <div class="card">
            <div class="kpi-title">Mejor performance</div>
            <div class="kpi-value">{insights['best_perf_producto']}</div>
            <div class="kpi-sub">{insights['best_perf_val']:.1%}</div>
        </div>
        """

    # ✅ gráfico performance
    perf_img_html = ""

    if chart_paths.get("perf_producto"):
        perf_img_html = f"""
        <div class="panel">
            <h3>% sobre promedio</h3>
            {img_tag(chart_paths['perf_producto'])}
        </div>
        """

    
    vs_presup_30d_html = ""

    if chart_paths.get("ventas_vs_presupuesto_30d"):
        vs_presup_30d_html = f"""
        <div class="panel-wide">
            <h3>Ventas vs Presupuesto (Últimos 30 días)</h3>
            {img_tag(chart_paths['ventas_vs_presupuesto_30d'])}
        </div>
        """
    
    vs_presup_mensual_html = ""

    if chart_paths.get("ventas_vs_presupuesto_mensual"):
        vs_presup_mensual_html = f"""
        <div class="panel-wide">
            <h3>Ventas vs Presupuesto Mensual</h3>
            {img_tag(chart_paths['ventas_vs_presupuesto_mensual'])}
        </div>
        """



    # ✅ HTML
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Dashboard</title>

        <style>
            body {{
                font-family: Arial;
                margin: 0;
                background: #f4f6f9;
                color: #1f2937;
            }}

            .container {{
                max-width: 1200px;
                margin: auto;
                padding: 30px;
            }}

            .title {{
                font-size: 28px;
                font-weight: bold;
            }}

            .subtitle {{
                color: #6b7280;
                margin-bottom: 20px;
            }}

            /* KPI */
            .grid-kpi {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-bottom: 30px;

                background: #f4f6f9;

                padding-top: 10px;
                padding-bottom: 10px;
            }}

            .card {{
                background: white;
                padding: 16px;
                border-radius: 10px;
                box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            }}

            .kpi-title {{
                font-size: 14px;
                color: #6b7280;
            }}

            .kpi-value {{
                font-size: 22px;
                font-weight: bold;
            }}

            .kpi-sub {{
                margin-top: 5px;
                font-size: 13px;
            }}

            /* Insight */
            .insight {{
                background: #eef6ff;
                border-left: 5px solid #2563eb;
                padding: 16px;
                margin-bottom: 30px;
                border-radius: 8px;
            }}

            /* GRID DE GRÁFICOS */
            .grid-charts {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                gap: 20px;
            }}

            .panel {{
                background: white;
                padding: 16px;
                border-radius: 10px;
                box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            }}

            .panel-wide {{
                background: white;
                padding: 16px;
                border-radius: 10px;   
                box-shadow: 0 3px 8px rgba(0,0,0,0.08);

                grid-column: 1 / -1;
            }}

            h3 {{
                margin-top: 0;
            }}

            .sticky-header {{
                position: sticky;
                top: 0;
                z-index: 200;

                background: #f4f6f9;

                padding-top: 10px;
                padding-bottom: 10px;

                box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            }}

        </style>

    </head>

    <body>

    <div class="container">

        <div class="sticky-header">

            <div class="title">📊 Dashboard de ventas</div>
            <div class="subtitle">
                Última fecha: {insights['ultimo_dia'].date()}
            </div>
        
            <!-- KPIs -->
            <div class="grid-kpi">

            <div class="card">
                <div class="kpi-title">Producto líder</div>
                <div class="kpi-value">{insights['top_producto']}</div>
                <div class="kpi-sub">{insights['top_producto_val']:,.0f}</div>
            </div>

            <div class="card">
                <div class="kpi-title">Región líder</div>
                <div class="kpi-value">{insights['top_region']}</div>
                <div class="kpi-sub">{insights['top_region_val']:,.0f}</div>
            </div>

            <div class="card">
                <div class="kpi-title">Ventas último día</div>
                <div class="kpi-value">{insights['ventas_ultimo_dia']:,.0f}</div>
                <div class="kpi-sub">{insights['ultimo_dia'].date()}</div>
                {delta_html}
            </div>

            {best_perf_card}
            {presupuesto_card}

            </div>  <!-- cierre grid-kpi -->

        </div>      <!-- cierre sticky-header -->

        <!-- Insight -->
        <div class="insight">
            <b>Insight:</b>
            {insights['top_producto']} lidera ventas y la región {insights['top_region']} domina el mercado.
        </div>

        <!-- GRÁFICOS EN GRID -->
        <div class="grid-charts">

            <div class="panel">
                <h3>Ventas por producto</h3>
                {img_tag(chart_paths.get("ventas_producto"))}
            </div>

            <div class="panel">
                <h3>Ventas por región</h3>
                {img_tag(chart_paths.get("ventas_region"))}
            </div>

            <div class="panel">
                <h3>Evolución diaria</h3>
                {img_tag(chart_paths.get("ventas_dia"))}
            </div>

            {perf_img_html}

            {vs_presup_30d_html}

            {vs_presup_mensual_html}

        </div>

    </div>

    </body>
    </html>
    """

    # ✅ guardar
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)