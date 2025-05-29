import pandas as pd
import time
import random
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import numpy as np

df = pd.read_csv('links_propiedades_remax.csv', sep=';')
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

        titulo = soup.find("div", id="title")
        valor_alquiler = soup.find("div", class_="flex-start-center", id="price-container")
        expensas = soup.find("div", class_="flex-start-center", id="expenses-container")
        ubicacion = soup.find("p", {"id": "ubication-text"})
        direccion = soup.find("p", {"id": "ubication-text"})

        div_metros = soup.find("div", {"data-info": "dimensionTotalBuilt", "class": "feature"})
        metros_cuadrados = div_metros.find("span", class_="bold") if div_metros else None

        div_ambientes = soup.find("div", {"data-info": "totalRooms", "class": "feature"})
        ambientes = div_ambientes.find("span", class_="bold") if div_ambientes else None

        div_dormitorios = soup.find("div", {"data-info": "bedrooms", "class": "feature"})
        dormitorios = div_dormitorios.find("span", class_="bold") if div_dormitorios else None

        div_baños = soup.find("div", {"data-info": "bathrooms", "class": "feature"})
        baños = div_baños.find("span", class_="bold") if div_baños else None

        div_cocheras = soup.find("div", {"data-info": "parkingSpaces", "class": "feature"})
        cocheras = div_cocheras.find("span", class_="bold") if div_cocheras else None

        div_antiguedad = soup.find("div", {"data-info": "antiquity", "class": "feature"})
        años_antiguedad = div_antiguedad.find("span", class_="bold") if div_antiguedad else None

        coordenadas = soup.find("div", class_="place-name")

        def extraer_barrio(lugar):
            partes = lugar.split(',')
            if len(partes) >= 2:
                return partes[-2].strip()
            return np.nan

        barrio = extraer_barrio(ubicacion.text) if ubicacion else np.nan

        descripcion_larga = soup.find("h3", id="last")
        descripcion = descripcion_larga.text.strip() if descripcion_larga else ""

        datos_lista.append({
            "Link": url,
            "Título": titulo.text.strip() if titulo else np.nan,
            "Valor Alquiler": valor_alquiler.text.strip() if valor_alquiler else np.nan,
            "Expensas": expensas.text.replace("Expensas :", "").strip() if expensas else np.nan,
            "Barrio": barrio,
            "Dirección": direccion.text.strip() if direccion else np.nan,
            "Metros Cuadrados": metros_cuadrados.text.strip() if metros_cuadrados else np.nan,
            "Ambientes": ambientes.text.strip() if ambientes else np.nan,
            "Dormitorios": dormitorios.text.strip() if dormitorios else 0,
            "Baños": baños.text.strip() if baños else np.nan,
            "Cocheras": cocheras.text.strip() if cocheras else 0,
            "Años de Antigüedad": años_antiguedad.text.strip() if años_antiguedad else np.nan,
            "Coordenadas": coordenadas.text.strip() if coordenadas else np.nan,
            "Descripción": descripcion,
        })

        print(f"Extraído título de {url}: {titulo.text.strip() if titulo else '[SIN TÍTULO]'}")

    except Exception as e:
        print(f"Error en {url}: {e}")

df_resultado = pd.DataFrame(datos_lista)
df_resultado.to_csv("prueba_remax.csv", index=False, encoding="utf-8-sig", sep=";")
print("Extracción finalizada.")
