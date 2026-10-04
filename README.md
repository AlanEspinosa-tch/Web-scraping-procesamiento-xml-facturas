# Automatización de Web Scraping y procesamiento de CFDI/XML

Proyecto en Python para automatizar la recuperación de documentos desde un portal web y transformar archivos XML de facturación en información tabular para análisis y reportes.

## Objetivo

Automatizar tareas repetitivas de descarga, lectura, filtrado y consolidación de CFDI/XML.

## Flujo

```
Portal web
    ↓
Automatización del navegador
    ↓
Archivos XML
    ↓
Validación y filtrado
    ↓
Extracción de información
    ↓
Base tabular
    ↓
Reporte en Excel
```

## Mi contribución

Definí:

- el flujo operativo;
- las reglas de filtrado;
- los mapeos necesarios para estandarizar la información;
- la estructura del resultado;
- las validaciones del proceso.

La implementación y optimización de parte del código Python se realizó con asistencia de herramientas de Inteligencia Artificial.

## Tecnologías

- Python
- Selenium WebDriver
- XML / `xml.etree.ElementTree`
- Pandas
- OpenPyXL
- procesamiento paralelo con `ProcessPoolExecutor`

## Confidencialidad

Los CFDI, datos fiscales, archivos descargados y resultados reales de la empresa no forman parte de la versión pública del proyecto.

Para reproducir el flujo públicamente se recomienda utilizar XML de ejemplo o datos sintéticos.
