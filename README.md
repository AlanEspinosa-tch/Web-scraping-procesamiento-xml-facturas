# Automatización de Web Scraping y Procesamiento de XMLs (CFDI)

Herramienta en Python diseñada para automatizar un flujo operativo completo: la extracción masiva de facturas electrónicas desde portales web mediante automatización de navegador, seguida por el procesamiento analítico y síntesis de los archivos XML en un reporte ejecutivo en Excel listo para el área de tesorería y finanzas.

##  Objetivo del Proyecto
Eliminar por completo la descarga manual de documentos y la captura repetitiva de datos fiscales, automatizando la recuperación de archivos y su posterior transformación en una base de datos tabular estructurada.

## 🧠 Arquitectura y Lógica de Negocio (Mi Contribución Principal)
Como Analista Financiero e Ingeniero Matemático, diseñé el requerimiento, la lógica y las reglas de validación implementadas:
*   **Automatización de Extracción (`webscraping.py`):** Estructuración del proceso de navegación web mediante Selenium y Firefox (Geckodriver), configurando directorios de descarga y control de tiempos de espera por snapshots para asegurar un flujo continuo sin interrupciones[cite: 3].
*   **Reglas de Filtrado y Negocio (`FACTURAS.py`):** 
    *   Validación estricta de comprobantes (filtrado por tipo ingreso "I", uso de CFDI específico "G01" y exclusión de volúmenes mínimos)[cite: 2].
    *   Mapeo automatizado de estaciones y conversión de claves de productos a códigos y letras estandarizados de combustibles (Regular, Premium, Diésel)[cite: 2].
    *   Extracción rigurosa de nodos especiales de facturación como el complemento del **BOL (Bill of Lading)** y el Timbre Fiscal Digital (UUID)[cite: 2].
*   **Consolidación Tabular:** Transformación de la estructura anidada de múltiples XMLs en un formato plano y limpio exportado directamente a un archivo Excel (`Reportes_Tesoreria_Final.xlsx`)[cite: 3].

## Implementación Técnica
*Nota de transparencia: La definición del proceso operativo, el diseño de las reglas de negocio, los mapeos de estaciones y la lógica de validación de los XML fueron diseñados por mí. Los scripts ejecutables en Python fueron desarrollados con asistencia de Inteligencia Artificial para agilizar la escritura de la sintaxis.*

*   **Lenguaje:** Python[cite: 2, 3]
*   **Automatización Web:** Selenium WebDriver (Firefox / Geckodriver)[cite: 3].
*   **Procesamiento de Datos:** `xml.etree.ElementTree` para parseo de XML, `pandas` para estructuración tabular y `ProcessPoolExecutor` para procesamiento en paralelo[cite: 2, 3].
*   **Salida:** Automatización de reportes tabulares en Excel (`openpyxl`)[cite: 3].

## 🚀 Valor Operativo
Este desarrollo redujo horas de trabajo manual repetitivo a un proceso automatizado de un solo clic, asegurando cero errores humanos en la recolección y permitiendo contar con información fiscal y operativa consolidada de manera inmediata.
