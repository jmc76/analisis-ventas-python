# Business Analytics & FP&A Platform with Python

Proyecto desarrollado en Python para automatizar procesos de Business Analytics y Financial Planning & Analysis (FP&A).

La solución integra analítica comercial, presupuestación, flujo de fondos, forecasting financiero, análisis de rentabilidad y dashboards ejecutivos con actualización automática diaria.

---

## Objetivos

- Automatizar la actualización diaria de ventas.
- Generar presupuestos dinámicos.
- Comparar resultados reales contra presupuesto.
- Gestionar cuentas por cobrar.
- Analizar flujo de caja.
- Generar forecast financiero.
- Medir rentabilidad y márgenes.
- Publicar dashboards ejecutivos para negocio y finanzas.

---

### Commercial Dashboard

assets/dashboard.png

### FP&A Dashboard - Executive Overview

assets/dashboard_fpa_1.png

### FP&A Dashboard - Financial Detail

assets/dashboard_fpa_2.png

---

## Arquitectura

```text
Raw Sales Data
        ↓
Update Pipeline
        ↓
Historical Sales
        ↓
Budget Generation
        ↓
Dynamic Expenses
        ↓
Financial Module
        ↓
Accounts Receivable
        ↓
Cash Flow
        ↓
Cash Projection
        ↓
Forecast Scenarios
        ↓
P&L Statement
        ↓
Executive Dashboards
```

---

## Revenue Analytics

### Funcionalidades

- Ventas por producto
- Ventas por región
- KPIs comerciales
- Promedios históricos
- Presupuesto dinámico
- Budget vs Actual
- Análisis de desvíos
- Dashboard Comercial

### Archivos generados

```text
ventas_historico.csv
presupuesto_ventas.csv
ventas_vs_presupuesto.csv
resumen_presupuesto.csv
modelo_dashboard.csv
```

---

## Financial Planning & Analysis (FP&A)

### Accounts Receivable

- Condiciones de pago simuladas
- Recovery Rate
- Cash Conversion Rate
- DSO (Days Sales Outstanding)
- Aging de cuentas por cobrar

### Cash Management

- Cobranzas proyectadas
- Flujo de caja
- Caja proyectada
- Burn Rate
- Cash Runway

### Forecasting

- Escenario Pesimista
- Escenario Base
- Escenario Optimista

### Profitability

- Margen de Contribución
- EBITDA
- Resultado Neto
- Estado de Resultados (P&L)

### Dashboard FP&A

- KPIs financieros
- Aging
- Forecast
- Profitability
- Cash Management
- Gráfico de Evolución de Caja Proyectada

### Archivos generados

```text
ventas_historico_finanzas.csv
cobranzas_proyectadas.csv
flujo_caja.csv
caja_proyectada.csv
forecast_caja.csv
estado_resultados.csv
resumen_financiero.csv
kpis_tesoreria.csv
dashboard_fpa.html
```

---

## Model Improvement

Durante el desarrollo del módulo FP&A se detectó una inconsistencia financiera.

Inicialmente los gastos variables permanecían constantes mientras las ventas crecían diariamente. Esto generaba márgenes y resultados artificialmente elevados.

Para resolverlo se rediseñó la generación de gastos variables para que conceptos como:

- Marketing
- Logística
- Comisiones
- Packaging

evolucionen automáticamente en función de las ventas.

Esta mejora permitió obtener indicadores financieros más consistentes y realistas para forecasting, cash flow y análisis de rentabilidad.

---

## Automatización

Todo el proceso se encuentra automatizado mediante:

- Python
- Windows Task Scheduler

La ejecución diaria del pipeline actualiza automáticamente:

```text
Ventas
↓
Presupuesto
↓
Gastos
↓
Finanzas
↓
Cash Flow
↓
Caja
↓
Forecast
↓
P&L
↓
Dashboard Comercial
↓
Dashboard FP&A
```

---

## Tecnologías Utilizadas

- Python
- Pandas
- NumPy
- Chart.js
- HTML
- Git
- GitHub
- Windows Task Scheduler

---

## Próximas Mejoras

- Forecast operativo a 30/60/90 días
- Gráfico de Aging
- Waterfall de EBITDA
- Dashboard interactivo vía Power BI
- Escenarios financieros avanzados

---

## Autor

Juan Manuel Cintado

LinkedIn:
https://www.linkedin.com/in/jmc76/

