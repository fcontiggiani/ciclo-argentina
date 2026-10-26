"""Descarga, empalma y exporta las series del monitor de ciclos.

Genera ``data/series.json`` e incrusta los mismos datos en ``index.html`` a partir de:

* PIB trimestral desestacionalizado del INDEC, base 1993 (1993-2013) y base 2004
  (2004 en adelante), empalmado hacia atrás por tasas de variación;
* EMAE mensual desestacionalizado del INDEC (base 2004);
* Índice Líder del CIF-UTDT (archivo local ``data/raw/indice_lider_utdt.csv``).

Las series del INDEC se obtienen de la API de Series de Tiempo de Argentina
(https://apis.datos.gob.ar/series/api/). Los identificadores deben verificarse
periódicamente, porque pueden cambiar.

Uso
---
    python scripts/actualizar_datos.py            # descarga desde la API
    python scripts/actualizar_datos.py --offline  # usa solo data/raw/

Requiere Python >= 3.10, pandas >= 2.0 y requests >= 2.31.
"""

# ---------------------------------------------------------------------------
# Importaciones y configuración general
# ---------------------------------------------------------------------------
from __future__ import annotations  # Permite anotaciones de tipo modernas en Python 3.10

import argparse  # Lee los argumentos de la línea de comandos
import io  # Convierte el texto descargado en un archivo en memoria
import json  # Escribe el archivo JSON con las series
import re  # Localiza el bloque de datos dentro de index.html
from datetime import date  # Registra la fecha de actualización
from pathlib import Path  # Maneja rutas de archivos de forma portable

import pandas as pd  # Manipula las series de tiempo
import requests  # Descarga las series desde la API

RAIZ = Path(__file__).resolve().parents[1]  # Carpeta raíz del repositorio
RAW = RAIZ / "data" / "raw"  # Carpeta con las series crudas en CSV
SALIDA = RAIZ / "data" / "series.json"  # Copia de los datos en JSON (respaldo y descarga)
PAGINA = RAIZ / "index.html"  # Página autocontenida que lleva los datos incrustados
API = "https://apis.datos.gob.ar/series/api/series/"  # Endpoint de la API de series

# Identificadores de la API (verificar antes de usar: pueden cambiar)
IDS = {  # Diccionario archivo local -> identificador de serie
    "pib_base2004_trim.csv": "3.2_OGP_D_2004_T_17",  # PIB desestacionalizado, base 2004, trimestral
    "pib_base1993_trim.csv": "1.2_OGP_D_1993_T_17",  # PIB desestacionalizado, base 1993, trimestral
    "emae_desest_mensual.csv": "143.3_NO_PR_2004_A_31",  # EMAE desestacionalizado, base 2004, mensual
}


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------
def descargar_serie(serie_id: str) -> pd.DataFrame:
    """Descarga una serie completa de la API de Series de Tiempo.

    Parameters
    ----------
    serie_id : str
        Identificador de la serie en la API.

    Returns
    -------
    pandas.DataFrame
        Columnas ``indice_tiempo`` (fecha) y la columna de valores.
    """
    parametros = {"ids": serie_id, "format": "csv", "limit": 1000}  # Pide la serie completa en CSV (máximo de la API: 1000 filas)
    respuesta = requests.get(API, params=parametros, timeout=60)  # Realiza la solicitud HTTP
    respuesta.raise_for_status()  # Detiene el proceso si la API devuelve un error
    datos = pd.read_csv(io.StringIO(respuesta.text))  # Convierte el texto CSV en un DataFrame
    if datos.empty:  # Controla que la serie tenga observaciones
        raise ValueError(f"La serie {serie_id} no devolvió datos")  # Informa el problema
    return datos  # Devuelve la serie descargada


def actualizar_crudos() -> None:
    """Descarga las series del INDEC y reemplaza los CSV de ``data/raw``."""
    for archivo, serie_id in IDS.items():  # Recorre cada serie a descargar
        datos = descargar_serie(serie_id)  # Descarga la serie desde la API
        datos.to_csv(RAW / archivo, index=False)  # Guarda la versión cruda en CSV
        print(f"{archivo}: {len(datos)} observaciones")  # Informa cuántos datos se obtuvieron


# ---------------------------------------------------------------------------
# Lectura y empalme
# ---------------------------------------------------------------------------
def leer(archivo: str) -> pd.Series:
    """Lee un CSV de ``data/raw`` y devuelve una serie indexada por fecha."""
    datos = pd.read_csv(RAW / archivo, parse_dates=["indice_tiempo"])  # Lee el archivo con fechas
    serie = datos.set_index("indice_tiempo").iloc[:, 0]  # Toma la única columna de valores
    serie = serie.astype(float).dropna().sort_index()  # Asegura tipo numérico y orden temporal
    return serie  # Devuelve la serie lista para operar


def empalmar_hacia_atras(nueva: pd.Series, vieja: pd.Series) -> tuple[pd.Series, pd.Timestamp]:
    """Empalma la base vieja con la nueva conservando las tasas de la base vieja.

    Para t anterior al primer período de la base nueva (t0):
        Y_t = Y_t0(nueva) * Y_t(vieja) / Y_t0(vieja)

    Parameters
    ----------
    nueva : pandas.Series
        Serie en la base nueva (base 2004).
    vieja : pandas.Series
        Serie en la base anterior (base 1993), que debe incluir t0.

    Returns
    -------
    tuple
        Serie empalmada (en unidades de la base nueva) y fecha de empalme t0.
    """
    t0 = nueva.index.min()  # Primer trimestre disponible en la base nueva
    if t0 not in vieja.index:  # Controla que exista un período común
        raise ValueError("Las bases no tienen un período en común para empalmar")  # Informa el error
    factor = nueva.loc[t0] / vieja.loc[t0]  # Cociente entre niveles en el período de empalme
    retro = vieja.loc[vieja.index < t0] * factor  # Reescala la base vieja a pesos de 2004
    empalmada = pd.concat([retro, nueva]).sort_index()  # Une el tramo retropolado con la base nueva
    tasas_vieja = vieja.loc[vieja.index <= t0].pct_change().dropna()  # Tasas originales de la base vieja
    tasas_emp = empalmada.loc[empalmada.index <= t0].pct_change().dropna()  # Tasas del tramo empalmado
    assert (tasas_vieja - tasas_emp).abs().max() < 1e-12, "El empalme alteró las tasas de variación"  # Valida el método
    return empalmada, t0  # Devuelve la serie y la fecha de empalme


# ---------------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------------
def a_lista(serie: pd.Series, decimales: int) -> dict:
    """Convierte una serie en listas de fechas (AAAA-MM) y valores redondeados."""
    return {  # Estructura que lee la página
        "fechas": [f.strftime("%Y-%m") for f in serie.index],  # Fechas como texto año-mes
        "valores": [round(float(v), decimales) for v in serie.values],  # Valores redondeados
    }


def construir_json() -> dict:
    """Arma el diccionario con las tres series y sus metadatos."""
    pib04 = leer("pib_base2004_trim.csv")  # PIB base 2004
    pib93 = leer("pib_base1993_trim.csv")  # PIB base 1993
    pib, t0 = empalmar_hacia_atras(pib04, pib93)  # Serie larga empalmada en pesos de 2004
    emae = leer("emae_desest_mensual.csv")  # EMAE desestacionalizado
    lider = leer("indice_lider_utdt.csv")  # Índice Líder UTDT

    # Validaciones de frecuencia: trimestres de 3 meses y meses consecutivos
    assert pib.index.to_series().diff().dropna().dt.days.between(89, 92).all(), "PIB no trimestral"  # Control del PIB
    assert emae.index.to_series().diff().dropna().dt.days.between(28, 31).all(), "EMAE con huecos"  # Control del EMAE
    assert lider.index.to_series().diff().dropna().dt.days.between(28, 31).all(), "IL con huecos"  # Control del IL

    return {  # Estructura final del archivo series.json
        "actualizado": date.today().isoformat(),  # Fecha de generación del archivo
        "series": {  # Bloque de series
            "pib": {  # PIB empalmado
                "nombre": "PIB",  # Nombre corto para la interfaz
                "descripcion": "PIB a precios de 2004, desestacionalizado",  # Descripción
                "rol": "Referencia",  # Papel en el análisis del ciclo
                "frecuencia": "T",  # Frecuencia trimestral
                "unidad": "millones de $ de 2004",  # Unidad de medida
                "fuente": "INDEC, Cuentas nacionales (bases 1993 y 2004), vía API Series de Tiempo",  # Fuente
                "ids": [IDS["pib_base2004_trim.csv"], IDS["pib_base1993_trim.csv"]],  # Identificadores
                "nota": f"Empalme hacia atrás por tasas de la base 1993 en {t0:%Y-%m}",  # Nota metodológica
                **a_lista(pib, 1),  # Fechas y valores
            },
            "emae": {  # EMAE
                "nombre": "EMAE",  # Nombre corto
                "descripcion": "Estimador Mensual de Actividad Económica, desestacionalizado",  # Descripción
                "rol": "Coincidente",  # Papel en el análisis del ciclo
                "frecuencia": "M",  # Frecuencia mensual
                "unidad": "índice 2004 = 100",  # Unidad de medida
                "fuente": "INDEC, EMAE base 2004, vía API Series de Tiempo",  # Fuente
                "ids": [IDS["emae_desest_mensual.csv"]],  # Identificador
                "nota": "",  # Sin observaciones adicionales
                **a_lista(emae, 3),  # Fechas y valores
            },
            "il": {  # Índice Líder
                "nombre": "Índice Líder",  # Nombre corto
                "descripcion": "Índice Líder del CIF-UTDT",  # Descripción
                "rol": "Líder",  # Papel en el análisis del ciclo
                "frecuencia": "M",  # Frecuencia mensual
                "unidad": "índice 2004 = 100",  # Unidad de medida
                "fuente": "Centro de Investigación en Finanzas, Universidad Torcuato Di Tella",  # Fuente
                "ids": [],  # No proviene de la API
                "nota": f"Planilla histórica; último dato {lider.index.max():%Y-%m}",  # Vigencia de los datos
                **a_lista(lider, 3),  # Fechas y valores
            },
        },
    }


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def incrustar_en_pagina(texto_json: str) -> None:
    """Reemplaza el bloque <script id="datos-series"> de index.html por los datos nuevos."""
    html = PAGINA.read_text(encoding="utf-8")  # Lee la página completa
    patron = re.compile(r'(<script type="application/json" id="datos-series">)(.*?)(</script>)', re.S)  # Bloque de datos
    if not patron.search(html):  # Verifica que el bloque exista antes de reemplazar
        raise RuntimeError("index.html no contiene el bloque de datos 'datos-series'")  # Aborta sin tocar el archivo
    seguro = texto_json.replace("</", "<\\/")  # Escapa "</" para que el JSON no cierre la etiqueta <script>
    html = patron.sub(lambda m: m.group(1) + seguro + m.group(3), html, count=1)  # Sustituye solo el contenido
    PAGINA.write_text(html, encoding="utf-8")  # Guarda la página actualizada


def main() -> None:
    """Ejecuta la actualización completa."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])  # Define la interfaz de comandos
    parser.add_argument("--offline", action="store_true", help="no descargar; usar data/raw")  # Opción sin conexión
    args = parser.parse_args()  # Lee los argumentos recibidos
    if not args.offline:  # Si se pidió descargar
        actualizar_crudos()  # Actualiza los CSV crudos desde la API
    datos = construir_json()  # Arma el contenido del JSON
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))  # Serializa los datos en JSON compacto
    SALIDA.write_text(texto, encoding="utf-8")  # Escribe data/series.json
    incrustar_en_pagina(texto)  # Copia los mismos datos dentro de index.html
    for clave, s in datos["series"].items():  # Recorre las series exportadas
        print(f"{clave}: {s['fechas'][0]} a {s['fechas'][-1]} ({len(s['fechas'])} obs.)")  # Resume cada serie


if __name__ == "__main__":  # Ejecuta solo si el archivo se llama directamente
    main()  # Llama al programa principal
