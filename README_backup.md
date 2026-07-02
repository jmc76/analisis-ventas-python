# 📊 Dashboard automático de ventas con Python

Pipeline de datos desarrollado en Python que automatiza el análisis de ventas, genera KPIs y construye un dashboard HTML con insights de negocio.

---

## 📊 Ejemplo de dashboard generado

![Dashboard](assets/dashboard.png)

---

## 🚀 Descripción

Este proyecto procesa datos de ventas y genera automáticamente:

- KPIs de negocio
- Visualizaciones
- Insights ejecutivos
- Dashboard HTML

Incluye comparación vs día anterior para analizar evolución de performance.

---

## 🎯 Objetivo

Transformar datos en información accionable mediante automatización del reporting.

---

## ⚙️ Tecnologías utilizadas

- Python
- Pandas
- Matplotlib

---

## 📈 Funcionalidades principales

✔ Procesamiento automático  
✔ Cálculo de KPIs  
✔ Generación de gráficos  
✔ Insights de negocio  
✔ Dashboard HTML dinámico  
✔ Variación diaria de ventas  
✔ Control de calidad de datos  
✔ Pipeline idempotente (sin duplicación de cargas)  

---

## 🛡️ Mejora: control de duplicados en histórico

Durante el desarrollo del proyecto se detectó una inconsistencia en el histórico de ventas, donde un día presentaba un salto anómalo debido a múltiples ejecuciones del pipeline.

Se implementó una lógica de control de cargas que:

- Reemplaza registros por fecha en lugar de concatenarlos
- Evita reprocesamientos duplicados
- Garantiza consistencia en el histórico de datos
- Permite volver a ejecutar el pipeline sin afectar los resultados (idempotencia)

Esto permitió corregir un caso real de calidad de datos (22/05/2026), asegurando la confiabilidad del reporting.

---

## 📊 Output

El pipeline genera:

- Dashboard HTML: `output/reporte.html`
- Gráficos en `output/charts/`

Ejemplo:

output/dashboard_v3.png

---

## ▶️ Cómo ejecutar el proyecto

1. Clonar el repositorio:

```bash
git clone https://github.com/jmc76/analisis-ventas-python.git