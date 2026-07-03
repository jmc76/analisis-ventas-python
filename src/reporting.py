from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

def generar_graficas_y_insights(
    historico_path="data/processed/ventas_historico.csv",
    output_dir="output/charts"
):
    """
    Genera gráficas en PNG y devuelve insights en un diccionario.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(historico_path)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["ventas"] = pd.to_numeric(df["ventas"], errors="coerce")
    df = df.dropna(subset=["fecha", "ventas", "producto", "region"])

    # Archivo de comparación contra presupuesto
    presup_path = Path("output/ventas_vs_presupuesto.csv")

    df_presup = None

    if presup_path.exists():
        df_presup = pd.read_csv(presup_path)
        df_presup["fecha"] = pd.to_datetime(df_presup["fecha"])

    # Agregaciones
    ventas_producto = df.groupby("producto")["ventas"].sum().sort_values(ascending=False)
    ventas_region = df.groupby("region")["ventas"].sum().sort_values(ascending=False)
    ventas_dia = df.groupby("fecha")["ventas"].sum().sort_index()

    pct_sobre_prod = None
    if "venta_sobre_prom_producto" in df.columns:
        pct_sobre_prod = (
            df.groupby("producto")["venta_sobre_prom_producto"]
            .mean()
            .sort_values(ascending=False)
        )

    # ---------- Gráfica 1: Ventas por producto ----------
    plt.figure(figsize=(8, 5))
    
    ax = ventas_producto.plot(
        kind="bar",
        color="#2E86AB"
    )

    for i, v in enumerate(ventas_producto.values):
        ax.text(
            i,
            v * 1.01,
            f"{v/1000:,.0f}K",
            ha="center",
            fontsize=8
        )

    plt.grid(axis="y", alpha=0.3)
    plt.title("Ventas totales por producto")
    plt.xlabel("Producto")
    plt.ylabel("Ventas")
    plt.xticks(rotation=0)
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{x/1_000_000:.1f}M")
    )
    plt.tight_layout()
    path_ventas_producto = output_path / "ventas_producto.png"
    plt.savefig(path_ventas_producto, dpi=150)
    plt.close()

    # ---------- Gráfica 2: Ventas por región ----------
    plt.figure(figsize=(8, 5))
    
    ax = ventas_region.plot(
        kind="bar",
        color="#F18F01"
    )

    for i, v in enumerate(ventas_region.values):
        ax.text(
            i,
            v * 1.01,
            f"{v/1000:,.0f}K",
            ha="center",
            fontsize=8
        )


    plt.title("Ventas totales por región")
    plt.xlabel("Región")
    plt.ylabel("Ventas")
    plt.xticks(rotation=0)
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{x/1_000_000:.1f}M")
    )
    plt.grid(
        axis="y",
        alpha=0.3
    )
    plt.tight_layout()
    path_ventas_region = output_path / "ventas_region.png"
    plt.savefig(path_ventas_region, dpi=150)
    plt.close()

    # ---------- Gráfica 3: Tendencia diaria ----------
    plt.figure(figsize=(10, 5))

    ax = ventas_dia.plot(
        color="#6A994E",
        linewidth=2
    )

    # Destacar último día
    ultimo_dia = ventas_dia.index[-1]
    ultima_venta = ventas_dia.iloc[-1]

    plt.scatter(
        ultimo_dia,
        ultima_venta,
        color="red",
        s=60,
        zorder=5
    )

    plt.annotate(
        f"{ultima_venta/1000:,.0f}K",
        (ultimo_dia, ultima_venta),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8
    )

    plt.title("Evolución diaria de ventas")
    plt.xlabel("Fecha")
    plt.ylabel("Ventas")

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{x/1000:,.0f}K")
    )

    plt.xticks(rotation=45)

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    path_ventas_dia = output_path / "ventas_dia.png"

    plt.savefig(path_ventas_dia, dpi=150)
    plt.close()

    # ---------- Gráfica 4: Ventas vs Presupuesto (últimos 30 días) ----------

    path_vs_presup_30d = None

    if df_presup is not None:

        ultimos_30 = df_presup.sort_values("fecha").tail(30)

        plt.figure(figsize=(10, 5))

        plt.plot(
            ultimos_30["fecha"],
            ultimos_30["ventas_reales"],
            label="Ventas reales",
            linewidth=2
        )

        plt.plot(
            ultimos_30["fecha"],
            ultimos_30["venta_presupuestada"],
            label="Presupuesto",
            linestyle="--",
            linewidth=2
        )

        plt.title("Ventas reales vs presupuesto (últimos 30 días)")
        plt.xlabel("Fecha")
        plt.ylabel("Ventas")
        plt.legend()
        
        
        ax = plt.gca()

        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda x, pos: f"{x/1000:,.0f}K")
        )

        plt.xticks(rotation=45)

        plt.grid(
            axis="y",
            alpha=0.3
        )

        plt.tight_layout()

        path_vs_presup_30d = output_path / "ventas_vs_presupuesto_30d.png"

        plt.savefig(path_vs_presup_30d, dpi=150)
        plt.close()
      
    # ---------- Gráfica 5: Ventas vs Presupuesto mensual ----------

    path_vs_presup_mensual = None

    if df_presup is not None:

        mensual = df_presup.copy()

        mensual["mes"] = mensual["fecha"].dt.to_period("M")

        mensual = (
            mensual.groupby("mes")
            .agg(
                ventas_reales=("ventas_reales", "sum"),
                venta_presupuestada=("venta_presupuestada", "sum")
            )
            .reset_index()
        )

        mensual["mes"] = mensual["mes"].astype(str)

        plt.figure(figsize=(10, 5))

        x = range(len(mensual))
        ancho = 0.4

        plt.bar(
            [i - ancho/2 for i in x],
            mensual["ventas_reales"],
            width=ancho,
            label="Ventas reales",
            color="#2E86AB"
        )
          
        for i, v in enumerate(mensual["ventas_reales"]):
            plt.text(
                i - ancho/2,
                v,
                f"{v/1000:,.0f}K",
                ha="center",
                fontsize=8
            )


        plt.bar(
            [i + ancho/2 for i in x],
            mensual["venta_presupuestada"],
            width=ancho,
            label="Presupuesto",
            color="#F18F01"
        )
          
        for i, v in enumerate(mensual["venta_presupuestada"]):
            plt.text(
                i + ancho/2,
                v,
                f"{v/1000:,.0f}K",
                ha="center",
                fontsize=8
            )


        plt.xticks(x, mensual["mes"], rotation=45)
        plt.title("Ventas reales vs presupuesto mensual")
        plt.ylabel("Ventas")

        
        ax = plt.gca()

        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda x, pos: f"{x/1_000_000:.1f}M")
        )

        plt.grid(
            axis="y",
            alpha=0.3
        )

        plt.legend()
        plt.tight_layout()

        path_vs_presup_mensual = (
            output_path / "ventas_vs_presupuesto_mensual.png"
        )

        plt.savefig(path_vs_presup_mensual, dpi=150)
        plt.close()
    
    # ---------- Gráfica 4: % sobre promedio ----------
    path_perf_producto = None
    if pct_sobre_prod is not None:
        # Convertimos booleanos a proporción si vinieran como bool directo
        plt.figure(figsize=(8, 5))
        
        ax = pct_sobre_prod.plot(
            kind="bar",
            color="#9B5DE5"
        )

        for i, v in enumerate(pct_sobre_prod.values):

            ax.text(
                i,
                v * 1.01,
                f"{v:.1%}",
                ha="center",
                fontsize=8
            )
        
        ax.yaxis.set_major_formatter(
            PercentFormatter(1)
        )

        plt.grid(
            axis="y",
            alpha=0.3
        )

        plt.title("Ranking de productos (% sobre promedio)")
        plt.xlabel("Producto")
        plt.ylabel("Proporción")
        plt.xticks(rotation=0)
        plt.tight_layout()
        path_perf_producto = output_path / "perf_producto.png"
        plt.savefig(path_perf_producto, dpi=150)
        plt.close()

    # ---------- Insights ----------
    top_prod = ventas_producto.index[0]
    top_prod_val = ventas_producto.iloc[0]

    top_reg = ventas_region.index[0]
    top_reg_val = ventas_region.iloc[0]

    ultimo_dia = ventas_dia.index.max()
    ventas_ultimo = ventas_dia.loc[ultimo_dia]

    insights = {
        "top_producto": top_prod,
        "top_producto_val": float(top_prod_val),
        "top_region": top_reg,
        "top_region_val": float(top_reg_val),
        "ultimo_dia": ultimo_dia,
        "ventas_ultimo_dia": float(ventas_ultimo),
        "best_perf_producto": None,
        "best_perf_val": None,

    # ✅ NUEVO (clave para variación diaria)
    "serie_fechas": list(ventas_dia.index),
    "serie_ventas": [float(v) for v in ventas_dia.values]
    }

    if pct_sobre_prod is not None:
        insights["best_perf_producto"] = pct_sobre_prod.index[0]
        insights["best_perf_val"] = float(pct_sobre_prod.iloc[0])

    chart_paths = {

        "ventas_vs_presupuesto_30d": (
            str(path_vs_presup_30d)
            if path_vs_presup_30d
            else None
        ),

        "ventas_vs_presupuesto_mensual": (
            str(path_vs_presup_mensual)
            if path_vs_presup_mensual
            else None
        ),

        "ventas_producto": str(path_ventas_producto),
        "ventas_region": str(path_ventas_region),
        "ventas_dia": str(path_ventas_dia),
        "perf_producto": str(path_perf_producto) if path_perf_producto else None
    }

    return insights, chart_paths