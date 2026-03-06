# SmartReport

SmartReport es una aplicación de escritorio desarrollada en **Python** que permite analizar datasets automáticamente y generar **reportes visuales en PDF y HTML** a partir de archivos de datos.

La aplicación incluye una **interfaz gráfica moderna**, un **visor interactivo del dataset**, herramientas de **búsqueda, filtrado y edición**, y un sistema automático de **análisis estadístico con visualizaciones**.

Este proyecto fue desarrollado como herramienta para **automatizar el análisis exploratorio de datos (EDA)** y facilitar la generación rápida de reportes.

---

# Features

## Carga de datos

Soporta múltiples formatos:

- CSV  
- Excel (.xlsx / .xls)  
- JSON  

El sistema detecta automáticamente las **columnas numéricas** disponibles para análisis.

---

# Dataset Preview

La aplicación incluye una **vista previa interactiva del dataset** con:

- Visualización de hasta **10.000 filas**
- Búsqueda por columna
- Ordenamiento por columnas
- Edición de celdas
- Marcado visual de filas
- Exportación de copia modificada

### Marcado de filas

- **Click izquierdo** → marcar fila en verde  
- **Click derecho** → marcar fila en rojo  

Esto permite identificar rápidamente datos relevantes o problemáticos durante el análisis.

---

# Análisis automático

Para cada columna numérica seleccionada SmartReport calcula:

- Total
- Promedio
- Mínimo
- Máximo
- Desviación estándar

También realiza detección automática de **valores atípicos (Outliers)** usando:

- Q1
- Q3
- IQR
- Límites inferior y superior

El sistema genera un **insight automático** sobre la estabilidad de la distribución.

---

# Visualizaciones

Para cada columna analizada se generan automáticamente:

- Histogramas de distribución
- Boxplots de dispersión

Estas visualizaciones se incluyen dentro de los reportes generados.

---

# Generación de reportes

SmartReport permite exportar análisis completos en:

## PDF

Incluye:

- métricas estadísticas
- histogramas
- estructura de reporte organizada por columnas

## HTML

Reporte visual moderno con:

- métricas destacadas
- insights automáticos
- histogramas
- boxplots
- diseño visual moderno

---

# Technologies Used

- Python
- Pandas
- Matplotlib
- CustomTkinter
- ReportLab
- Tkinter / TTK

---

# Flujo de uso:

1. Seleccionar un archivo de datos  
2. Visualizar el dataset en la ventana de preview  
3. Elegir columnas numéricas a analizar  
4. Generar reporte en **PDF o HTML**

