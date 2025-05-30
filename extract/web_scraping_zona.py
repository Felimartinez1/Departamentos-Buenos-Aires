import pandas as pd
import time
import random
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import re
import numpy as np

def extraer_numero(texto):
    if not texto:
        return np.nan
    numeros = re.findall(r'\d+', texto)
    return numeros[0] if numeros else np.nan

df = pd.read_csv('links_propiedades_zona.csv', sep=';')
urls = df['Link'].dropna().tolist()

print(f"Probando con {len(urls)} links...")

browser = uc.Chrome()
datos_lista = []

for url in urls:
    try:
        browser.get(url)
        time.sleep(random.randint(8, 10))

        body = browser.find_element("tag name", "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

        html = browser.page_source
        soup = bs(html, 'lxml')

        titulo = soup.find("div", class_="section-title")
        valor_alquiler = soup.find("div", class_="price-value")
        expensas = soup.find("span", class_="price-expenses")
        descripcion_div = soup.find("div", id="longDescription")

        ubicacion_container = soup.find("div", class_="section-location-property section-location-property-classified")
        ubicacion = ubicacion_container.find("h4") if ubicacion_container else None
        direccion = ubicacion_container.find("h4") if ubicacion_container else None

        metros_cuadrados = ambientes = baños = años_antiguedad = np.nan
        dormitorios = cocheras = 0

        iconos = soup.find_all("li", class_="icon-feature")
        for li in iconos:
            icono = li.find("i")
            texto = ' '.join(li.stripped_strings)

            if icono:
                clases = icono.get("class", [])
                if "icon-stotal" in clases:
                    metros_cuadrados = extraer_numero(texto)
                elif "icon-ambiente" in clases:
                    ambientes = extraer_numero(texto)
                elif "icon-dormitorio" in clases:
                    dormitorios = extraer_numero(texto)
                elif "icon-bano" in clases:
                    baños = extraer_numero(texto)
                elif "icon-cochera" in clases:
                    cocheras = extraer_numero(texto)
                elif "icon-antiguedad" in clases:
                    años_antiguedad = extraer_numero(texto)

        coordenadas = soup.find("div", class_="place-name")

        def extraer_barrio(direccion):
            partes = direccion.split(',')
            if len(partes) >= 2:
                return partes[-2].strip()
            return np.nan

        barrio = extraer_barrio(' '.join(ubicacion.stripped_strings)) if ubicacion else np.nan

        datos_lista.append({
            "Título": ' '.join(titulo.stripped_strings) if titulo else np.nan,
            "Descripción": ' '.join(descripcion_div.stripped_strings) if descripcion_div else np.nan,
            "Valor Alquiler": ' '.join(valor_alquiler.stripped_strings) if valor_alquiler else np.nan,
            "Expensas": expensas.text.replace("Expensas:", "").strip() if expensas else np.nan,
            "Barrio": barrio,
            "Dirección": ' '.join(direccion.stripped_strings) if direccion else np.nan,
            "Metros Cuadrados": metros_cuadrados,
            "Ambientes": ambientes,
            "Dormitorios": dormitorios,
            "Baños": baños,
            "Cocheras": cocheras,
            "Años de Antigüedad": años_antiguedad, 
            "Coordenadas": ' '.join(coordenadas.stripped_strings) if coordenadas else np.nan,
            "Link": url, ### SIEMPRE DEJAR LINK AL FINAL
        })

        print(f"Extraído título de {url}: {' '.join(titulo.stripped_strings) if titulo else '[SIN TÍTULO]'}")

    except Exception as e:
        print(f"Error en {url}: {e}")

df_resultado = pd.DataFrame(datos_lista)
df_resultado.to_csv("prueba_zona.csv", index=False, encoding="utf-8-sig", sep=";")
print("Extracción finalizada.")
