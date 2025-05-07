import requests
from bs4 import BeautifulSoup as bs
import random
import time
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

# Configurar opciones de Chrome
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
# Descomenta la siguiente línea si querés que se ejecute en segundo plano (sin abrir ventana)
# options.add_argument("--headless")

# Iniciar navegador, especificando la versión de Chrome (135 en tu caso actual)
try:
    browser = uc.Chrome(options=options, version_main=135)
except Exception as e:
    print(f"Error al iniciar Chrome: {e}")
    exit()

# Aclarar la URL principal
url = "https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-pagina-2.html"
max_paginas = 471
x = 2

datos_lista = []

while x <= max_paginas:
    if x == 471:
        print("Se alcanzó la última página, finalizando ejecución.")
        break

    url = f'https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-pagina-{x}.html'
    print(f"Scrapeando página {x}...")

    try:
        browser.get(url)
        time.sleep(random.randint(10, 12))  # Pausa para evitar detección

        # Scroll hacia abajo
        body = browser.find_element("tag name", "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.randint(2, 4))

        # Hacer click en el botón de cookies automáticamente (solo la primera vez generalmente)
        try:
            browser.find_element("xpath", '//button[@data-qa="cookies-policy-banner"]').click()
        except:
            pass

        # Obtener el HTML y parsear con BeautifulSoup
        html = browser.page_source
        soup = bs(html, 'lxml')

        # Verificar que estamos en la página esperada
        try:
            pagina_actual = int(
                soup.find("div", class_="paging-module__container-paging")
                .find("a", class_="paging-module__page-item paging-module__page-item-current")
                .text
            )
        except:
            print(f"⚠️ No se pudo determinar la página actual en la página {x}. Continuando...")
            pagina_actual = x  # En caso de error, igual intenta extraer datos

        if x == pagina_actual:
            propiedades = soup.find_all("div", class_="postingCard-module__posting-container")

            for propiedad in propiedades:
                # Extraer datos principales
                titulo = propiedad.find(
                    "div", class_="postingLocations-module__location-address postingLocations-module__location-address-in-listing")
                valor_alquiler = propiedad.find(
                    "div", class_="postingPrices-module__price", attrs={"data-qa": "POSTING_CARD_PRICE"})
                ubicacion = propiedad.find(
                    "h2", class_="postingLocations-module__location-text", attrs={"data-qa": "POSTING_CARD_LOCATION"})
                expensas = propiedad.find(
                    "div", class_="postingPrices-module__expenses postingPrices-module__expenses-property-listing")

                # Extraer características
                caracteristicas = propiedad.find(
                    "h3", class_="postingMainFeatures-module__posting-main-features-block postingMainFeatures-module__posting-main-features-block-one-line")
                datos = caracteristicas.find_all(
                    "span", class_="postingMainFeatures-module__posting-main-features-span postingMainFeatures-module__posting-main-features-listing"
                ) if caracteristicas else []

                # Inicializar categorías
                metros_cuadrados = 0
                ambientes = 0
                dormitorios = 0
                baños = 0
                cocheras = 0

                # Clasificar los datos
                for dato in datos:
                    text = dato.text.strip().lower()
                    if "m² tot" in text:
                        metros_cuadrados = int(text.split()[0])
                    elif "amb" in text:
                        ambientes = int(text.split()[0])
                    elif "dorm" in text:
                        dormitorios = int(text.split()[0])
                    elif "baño" in text or "baños" in text:
                        baños = int(text.split()[0])
                    elif "coch" in text:
                        cocheras = int(text.split()[0])

                datos_lista.append({
                    "Título": titulo.text.strip() if titulo else "No disponible",
                    "Ubicación": ubicacion.text.strip() if ubicacion else "No disponible",
                    "Valor Alquiler": valor_alquiler.text.strip() if valor_alquiler else "No disponible",
                    "Expensas": expensas.text.strip() if expensas else "No disponible",
                    "Metros Cuadrados": metros_cuadrados,
                    "Ambientes": ambientes,
                    "Dormitorios": dormitorios,
                    "Baños": baños,
                    "Cocheras": cocheras
                })

            print(f"✅ Datos extraídos de la página {x}.")
            x += 1
        else:
            print(f"⚠️ La página cargada no coincide (esperada: {x}, actual: {pagina_actual}). Retentando...")
            x += 1

    except Exception as e:
        print(f"❌ Error en la página {x}: {e}")
        x += 1  # Salta a la siguiente para no romper el bucle

# Crear dataframe y guardarlo en CSV
df = pd.DataFrame(datos_lista)
df.to_csv("Alquileres.csv", index=False, encoding="utf-8-sig", sep=";")

print("✅ Datos extraídos y guardados en 'Alquileres.csv'.")
