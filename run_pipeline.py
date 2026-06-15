import os
from datetime import datetime

# ✅ TEST: confirma que el Task Scheduler ejecutó este script
with open("test_scheduler.txt", "w", encoding="utf-8") as f:
    f.write(f"Se ejecutó run_pipeline.py: {datetime.now()}\n")

print("🚀 Iniciando pipeline...")

try:
    print("📥 Generando datos diarios...")
    os.system("python src/run_generate_daily.py")

    print("⚙️ Ejecutando pipeline...")
    os.system("python src/update_pipeline.py")

    print("✅ Pipeline completado correctamente")

except Exception as e:
    print("❌ Error en el pipeline:", e)


import sys
sys.exit(0)

