import pandas as pd
from generate_daily import generar_datos_dia, guardar_csv_diario

hoy = pd.Timestamp.today().normalize()
df = generar_datos_dia(hoy, n=200)
ruta = guardar_csv_diario(df)

print("✅ Archivo diario generado:", ruta)