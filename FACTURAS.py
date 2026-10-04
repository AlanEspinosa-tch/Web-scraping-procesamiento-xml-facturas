from datetime import datetime
import xml.etree.ElementTree as ET
import os
ns = {
    'cfdi': 'http://www.sat.gob.mx/cfd/4',
    'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
}

fecha_inicio = datetime(2022, 1, 1)

mapeo_empresa = {
    'ABASTECEDORA AVE FENIX': 'AVE FENIX',
    'COMBULUB EL PILAR': 'COMBULUB',
    'SERVICIO HUEHUETOCA': 'HUEHUETOCA',
    'SERVICIO IXTAZACUALA': 'IXTAZACUALA',
    'GRUPO TREHER': 'TREHER T',
    'GRUPO TOREMEX': 'TOREMEX',
    'GRUPO GASOLINERO TH': 'TH',
    'SUPER SERVICIO AURORA': 'AURORA',
    'GRUPO Q L': 'QL',
    'GASOLINERA TEOLOYUCAN': 'TEOLOYUCAN'
}

mapeo_combustible_codigo = {
    '15101514': 3,
    '15101515': 2,
    '15101505': 1
}

mapeo_combustible_letra = {
    '15101514': 'Regular',
    '15101515': 'Premium',
    '15101505': 'Diesel'
}

def limpiar_texto(valor):
    if valor is None:
        return None
    return str(valor).replace('\xa0', '').strip().upper()

def a_numero(valor):
    """Convierte un texto a entero, quitando ceros a la izquierda. Retorna None si falla."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None

def fecha_a_excel(fecha):
    excel_start = datetime(1899, 12, 30)
    return (fecha - excel_start).days

def procesar_xml(ruta):
    try:
        tree = ET.parse(ruta)
        root = tree.getroot()
        nombre_archivo= os.path.splitext(os.path.basename(ruta))[0]

        tipo_comprobante = root.attrib.get('TipoDeComprobante')
        if tipo_comprobante != "I":
            return None

        timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
        if timbre is None:
            return None
        uuid = limpiar_texto(timbre.attrib.get('UUID'))

        folio       = a_numero(limpiar_texto(root.attrib.get('Folio')))
        forma_pago  = limpiar_texto(root.attrib.get('FormaPago'))
        metodo_pago = limpiar_texto(root.attrib.get('MetodoPago'))

        receptor_node = root.find('cfdi:Receptor', ns)
        if receptor_node is None:
            return None
        
        receptor = limpiar_texto(receptor_node.attrib.get('Nombre'))

        receptor_limpio = receptor.replace('"', '').replace("'", "").strip().upper()

        if receptor_limpio == "SUPER SERVICIO AILES":
            if nombre_archivo.startswith("C-1138"):
                empresa="ATB"
            elif nombre_archivo.startswith("C-1139"):
                empresa="ATEPO"
            else:
                empresa="Desconocido"
        else:
            empresa  = mapeo_empresa.get(receptor, receptor)

        concepto = root.find('.//cfdi:Concepto', ns)
        if concepto is None:
            return None

        cantidad = float(concepto.attrib.get('Cantidad', 0))
        if cantidad < 20:
            return None
        
        uso_cfdi = limpiar_texto(receptor_node.attrib.get('UsoCFDI'))
        if uso_cfdi != 'G01':
            return None
        
        valor_unitario = float(concepto.attrib.get('ValorUnitario', 0))
        clave          = concepto.attrib.get('ClaveProdServ')

        combustible_cod   = mapeo_combustible_codigo.get(clave)
        combustible_letra = mapeo_combustible_letra.get(clave)

        bol_node = root.find('.//{*}BOL')
        if bol_node is None:
            return None

        bol= a_numero(limpiar_texto(bol_node.attrib.get('NumerodelBOL')))
        fecha_bol_str = bol_node.attrib.get('FechaBOL')

        try:
            fecha_bol = datetime.strptime(fecha_bol_str, "%Y-%m-%d")
        except:
            fecha_bol = datetime.strptime(fecha_bol_str, "%m/%d/%Y %H:%M:%S")

        if fecha_bol < fecha_inicio:
            return None

        return {
            'UUID':                  uuid,
            'Empresa':               empresa,
            'factura':               folio,
            'Lts':                   cantidad,
            'CTO UNIT':              valor_unitario,
            'Combustible (Código)':  combustible_cod,
            'Combustible (Letra)':   combustible_letra,
            'Fecha Bol':             fecha_a_excel(fecha_bol),
            'BOL':                   bol,
            'Tipo de comprobante':   tipo_comprobante,
            'forma de pago':         forma_pago,
            'Método de pago':        metodo_pago
        }

    except Exception as e:
        print("Error en:", ruta, e)
        return None