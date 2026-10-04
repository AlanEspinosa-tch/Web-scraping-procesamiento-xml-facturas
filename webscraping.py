'''
#################################------------- NOTAS IMPORTANTES --------------------#####################################
# RECUERDE QUE PARA EL FUNCIONAMIENTO DEL CÓDIGO, ES NECESARIO QUE TENGA EN UNA MISMA CARPETA EL geckodriver.exe, el archivo .py webscraping.py(este), y FACTURAS.py
# El archivo de webscraping es para las descargas pero el de FACTURAS es para el tratamiento de los XML
# 1) Recuerde siempre cambiar la variable "service" de la linea 70 dependiendo de la maquina que lo use, vaya a donde se encuentra el geckodriver y dele copiar como ruta de acceso, y lo sustituye despues del r
# 2) de igual forma en la linea 63, busque el archivo de firefox que se installa en "Este equipo"-> "Windows(C:)"->... y copiar como ruta de acceso
# 3)Se requiere una calidad de internet buena, para que el flujo de descargas sea continuo y el programa no se salte todas las descargas 
# 4)En caso de darse algún error, llamar a Claudia.
# Se requiere firefox para el funcionamiento de este código, en caso de quererlo con chrome, solicitarle a una IA que haga el ajuste para el uso del chromedriver en lugar del geckodriver

#####################################---------------CAMBIOS EN CÓDIGO QUE LES PODRIÁN SERVIR---------------------------------##################3

1) El código decarga todas las facturas de tipo ingreso (no detecta cuales ya están canceladas) de un mes entero (el actual por defecto), por lo que no es apto para descargar en una sola corrida todo el año de x-estación
2)En caso de requerir las facturas de únicamente x-estaciones, esto se puede modificar en las lineas 46-49, dejando dentro de los corchetes y con el formato en el que está las claves de las estaciones que se requiera, por defecto, estarán todas.
3)En caso de requerir las facturas de un mes distinto al actual, identificar en la linea 156 la variable "mes_actual" (la variable mes_actual es el número del mes actual, vease las lineas 157-161 del código), cambiar la línea de código
de: "mes_actual =datetime.now().month"  a "mes_actual =n"  siendo n el numero del mes que se requiera (enero=1, febrero=2,marzo=3,...)
4) Si se quiere cambiar de año cambiar las lineas 170,175,178, por defecto tendrán el año en 2026, cambiarlas al año que gusten 

'''

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
import os
import shutil
import time
import pandas as pd

from FACTURAS import procesar_xml

# ---------------- CONFIG ----------------
url_login = "http://onlineapps.com.mx/benzin/rpsam/default.aspx"
url_cfdi  = "http://onlineapps.com.mx/benzin/rpsam/Cli/CliFE33.aspx"

usuario  = "C-1136"
password = "Aguila51"

###########################
estaciones = [
    "C-1131","C-1132","C-1133","C-1134","C-1135","C-1136",
    "C-1137","C-1138","C-1139","C-1140","C-1142","C-1143"
]

base_dir = os.path.join(os.path.expanduser("~"), "Downloads", "CFDI")
xml_dir  = os.path.join(base_dir, "XML")
pdf_dir  = os.path.join(base_dir, "PDF")

os.makedirs(xml_dir, exist_ok=True)
os.makedirs(pdf_dir, exist_ok=True)


if __name__ == "__main__":

    # ---------------- FIREFOX ----------------
    options = Options()
    options.binary_location =r"C:\Program Files\Mozilla Firefox\firefox.exe" #"C:\Program Files\Mozilla Firefox\firefox.exe"<- este es de la compu de ALDO 
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", base_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/xml, text/xml, application/pdf")
    options.set_preference("pdfjs.disabled", True)

    service =Service(r"C:\Users\TREHER\TRANSPORTES C MORALES C SA de CV\Finanzas Treher - Finanzas Grupo Treher\09. Facturas\Código PYTHON descarga FACTURAS\geckodriver.exe")# 
    driver  = webdriver.Firefox(service=service, options=options) #
    wait    = WebDriverWait(driver, 10)

    # ---------------- FUNCIONES SELENIUM ----------------

    def cambiar_a_frame_contenido():
        driver.switch_to.default_content()
        for frame in driver.find_elements(By.TAG_NAME, "frame"):
            driver.switch_to.frame(frame)
            try:
                driver.find_element(By.TAG_NAME, "body")
                return
            except:
                driver.switch_to.default_content()

    def esperar_descargas_completas(timeout=1200):
        """
        Monitorea la carpeta por snapshots (nombre + tamaño).
        No depende de .part ni de sleeps fijos.
        Termina cuando la carpeta deja de cambiar en 2 ciclos consecutivos
        y no hay archivos .part activos.
        """
        inicio = time.time()

        def snapshot():
            archivos = {}
            for f in os.listdir(base_dir):
                ruta_f = os.path.join(base_dir, f)
                if os.path.isfile(ruta_f):
                    try:
                        archivos[f] = os.path.getsize(ruta_f)
                    except:
                        archivos[f] = -1
            return archivos

        # Esperar a que aparezca al menos un archivo nuevo (señal de que empezó la descarga)
        snap_inicial = snapshot()
        while True:
            if snapshot() != snap_inicial:
                break
            if time.time() - inicio > 30:
                break  # si en 30s no apareció nada, continuar de todas formas
            time.sleep(1)

        # Esperar a que la carpeta deje de cambiar Y no haya .part
        estable = 0
        while True:
            snap1 = snapshot()
            time.sleep(3)
            snap2 = snapshot()

            hay_part = any(f.endswith(".part") for f in snap2)

            if snap1 == snap2 and not hay_part:
                estable += 1
                if estable >= 2:
                    print("  Descargas terminadas")
                    break
            else:
                estable = 0

            if time.time() - inicio > timeout:
                print("  Timeout alcanzado")
                break

    def cerrar_ventanas_extra():
        ventanas = driver.window_handles
        for ventana in ventanas[1:]:
            try:
                driver.switch_to.window(ventana)
                driver.close()
            except:
                pass
        driver.switch_to.window(ventanas[0])

    def organizar_descargas():
        for archivo in os.listdir(base_dir):
            ruta = os.path.join(base_dir, archivo)
            if archivo.lower().endswith(".xml"):
                shutil.move(ruta, os.path.join(xml_dir, archivo))
            elif archivo.lower().endswith(".pdf"):
                shutil.move(ruta, os.path.join(pdf_dir, archivo))

    def configurar_anio_y_mes():
        cambiar_a_frame_contenido()
        mes_actual = datetime.now().month
        meses = {
            1:"Enero", 2:"Febrero", 3:"Marzo",   4:"Abril",
            5:"Mayo",  6:"Junio",   7:"Julio",   8:"Agosto",
            9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"
        }

        anio_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'Anio')]"))
        )

        año="2026"
        # Seleccionar todo y escribir el año
        anio_input.click()
        anio_input.send_keys(Keys.CONTROL + "a")
        anio_input.send_keys(año)
        anio_input.send_keys(Keys.TAB)
        time.sleep(1.5)

        # Verificar que el año quedó escrito
        if anio_input.get_attribute("value") != año:
            anio_input.click()
            anio_input.send_keys(Keys.CONTROL + "a")
            anio_input.send_keys(año)
            anio_input.send_keys(Keys.TAB)  
            time.sleep(1.5)

        # Para enero: clic en Febrero primero para fijar el año, luego en Enero
        if mes_actual == 1:
            print("  Enero detectado: clic en Febrero primero para fijar el año...")
            wait.until(
                EC.element_to_be_clickable((By.XPATH, "//td[text()='Febrero']"))
            ).click()
            time.sleep(1)

        wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//td[text()='{meses[mes_actual]}']"))
        ).click()

    def abrir_cfdi():
        driver.get(url_cfdi)
        time.sleep(3)
        configurar_anio_y_mes()

    def procesar_estacion(clave):
        try:
            abrir_cfdi()
            cambiar_a_frame_contenido()
            input_clave = wait.until(EC.presence_of_element_located((By.ID, "idCliente")))
            input_clave.clear()
            input_clave.send_keys(clave)
            input_clave.send_keys(Keys.ENTER)
            time.sleep(3)
            cambiar_a_frame_contenido()
            wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Seleccionar Todos']"))
            ).click()
            wait.until(EC.element_to_be_clickable((By.ID, "Button1"))).click()
            print(f"  Descargando estación {clave}...")
            esperar_descargas_completas()
            cerrar_ventanas_extra()
            print(f"  Descarga completada {clave}")
            return True
        except Exception as e:
            print(f"  Error en {clave}: {e}")
            return False

    # ---------------- LOGIN ----------------
    driver.get(url_login)
    wait.until(EC.presence_of_element_located((By.ID, "Usuario"))).send_keys(usuario)
    driver.find_element(By.ID, "Password").send_keys(password)
    driver.find_element(By.ID, "Button2").click()
    print("Login ejecutado")
    time.sleep(3)

    # ---------------- DESCARGA ----------------
    for estacion in estaciones:
        print(f"\nProcesando {estacion}")
        procesar_estacion(estacion)

    # Espera final antes de cerrar Firefox
    print("\nEsperando que todas las descargas finalicen...")
    esperar_descargas_completas()
    organizar_descargas()

    print("Archivos organizados — Ruta XML:", xml_dir)
    driver.quit()
    print("Navegador cerrado")

    # ---------------- PROCESAMIENTO XML EN PARALELO ----------------
    print("\n--- PROCESANDO XMLs ---")

    archivos = [
        os.path.join(xml_dir, f)
        for f in os.listdir(xml_dir)
        if f.lower().endswith(".xml")
    ]

    with ProcessPoolExecutor() as executor:
        resultados = list(executor.map(procesar_xml, archivos))

    datos = [r for r in resultados if r is not None]
    df_final = pd.DataFrame(datos)

    for col in ['UUID', 'Empresa', 'factura', 'BOL', 'forma de pago', 'Método de pago']:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(str).str.replace('\xa0', '').str.strip()

    ruta_salida = os.path.join(base_dir, "Reporte_Tesoreria_Final.xlsx")
    df_final.to_excel(ruta_salida, index=False)

    print("Facturas procesadas:", len(df_final))
    print("Reporte generado:", ruta_salida)