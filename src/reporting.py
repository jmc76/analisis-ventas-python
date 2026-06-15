from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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
    ventas_producto.plot(kind="bar", color="#2E86AB")
    plt.title("Ventas totales por producto")
    plt.xlabel("Producto")
    plt.ylabel("Ventas")
    plt.xticks(rotation=0)
    plt.tight_layout()
    path_ventas_producto = output_path / "ventas_producto.png"
    plt.savefig(path_ventas_producto, dpi=150)
    plt.close()

    # ---------- Gráfica 2: Ventas por región ----------
    plt.figure(figsize=(8, 5))
    ventas_region.plot(kind="bar", color="#F18F01")
    plt.title("Ventas totales por región")
    plt.xlabel("Región")
    plt.ylabel("Ventas")
    plt.xticks(rotation=0)
    plt.tight_layout()
    path_ventas_region = output_path / "ventas_region.png"
    plt.savefig(path_ventas_region, dpi=150)
    plt.close()

    # ---------- Gráfica 3: Tendencia diaria ----------
    plt.figure(figsize=(10, 5))
    ventas_dia.plot(color="#6A994E")
    plt.title("Evolución diaria de ventas")
    plt.xlabel("Fecha")
    plt.ylabel("Ventas")
    plt.tight_layout()
    path_ventas_dia = output_path / "ventas_dia.png"
    plt.savefig(path_ventas_dia, dpi=150)
    plt.close()

    # ---------- Gráfica 4: % sobre promedio ----------
    path_perf_producto = None
    if pct_sobre_prod is not None:
        # Convertimos booleanos a proporción si vinieran como bool directo
        plt.figure(figsize=(8, 5))
        pct_sobre_prod.plot(kind="bar", color="#9B5DE5")
        plt.title("% de ventas sobre el promedio por producto")
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
        "ventas_producto": str(path_ventas_producto),
        "ventas_region": str(path_ventas_region),
        "ventas_dia": str(path_ventas_dia),
        "perf_producto": str(path_perf_producto) if path_perf_producto else None
    }

    return insights, chart_paths