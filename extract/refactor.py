import time
import random
import re
import argparse
import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# ---------------------------------------------------
# Solo para la parte de ZonaProp: undetected_chromedriver
# ---------------------------------------------------
import undetected_chromedriver as uc
import tempfile
from multiprocessing import freeze_support

def preload_driver_binary():
    """
    Precarga el ejecutable de undetected_chromedriver (descarga/parchea si es necesario)
    para que los procesos hijos no lo hagan simultáneamente.
    """
    # Creamos un Chrome y lo cerramos inmediatamente
    # con use_subprocess=False (para parchear el binario en disco).
    driver = uc.Chrome(use_subprocess=False)
    driver.quit()

def create_browser_zona(headless=False):
    """
    Crea una instancia de undetected_chromedriver evitando colisiones en Windows:
     - use_subprocess=False
     - user_multi_procs=True    (soporte para múltiples procesos)
     - cada llamada usa un user-data-dir distinto (tempfile)
     - admite headless
    """
    # Carpeta temporal única para el perfil
    tmp_profile = tempfile.mkdtemp(prefix="uc_profile_")
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={tmp_profile}")
    
    if headless:
        # "--headless" en Chrome 109+ puede requerir "--headless=new", pero se deja sin especificar "new" para compatibilidad.
        options.add_argument("--headless=new")
    # Bloquear recargas innecesarias o configuraciones extra (si quisieras acelerar más)
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    
    # Habilitamos soporte para múltiples procesos:
    return uc.Chrome(
        options=options,
        use_subprocess=False,
        user_multi_procs=True
    )


# ---------------------------------------------------
# Resto del scraper (Remax + ZonaProp)
# ---------------------------------------------------

# Constants
REMAX_BASE = "https://www.remax.com.ar"
REMAX_LISTING_URL = (
    "https://www.remax.com.ar/listings/rent?page={page}&pageSize=24"
    "&sort=-createdAt&in:operationId=2&in:eStageId=0,1,2,3,4"
    "&in:typeId=1,2,3,4,5,6,7,8&locations=in:CF@%3Cb%3ECapital%3C%2Fb%3E%20%3Cb%3EFederal%3C%2Fb%3E::::::"
    "&landingPath=&filterCount=1&viewMode=listViewMode"
)
ZONA_BASE = "https://www.zonaprop.com.ar"
ZONA_LISTING_URL = "https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-pagina-{page}.html"


# ------------------------------------------
# Browser setup (Remax)
# ------------------------------------------
def create_browser_remax(headless=True, driver_path=None):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")

    # Bloquear imágenes y CSS para acelerar la carga
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2
    }
    options.add_experimental_option("prefs", prefs)

    if driver_path:
        # Forzamos a que NO ejecute Selenium Manager
        service = Service(executable_path=driver_path, use_selenium_manager=False)
        return webdriver.Chrome(service=service, options=options)
    else:
        # Selenium Manager intentará descargar el driver correcto automáticamente
        return webdriver.Chrome(options=options)


# --------------------
# Utilidades comunes
# --------------------
def safe_find_text(soup_elem):
    return soup_elem.get_text(strip=True) if soup_elem else ""

def extraer_numero(texto):
    if not texto:
        return np.nan
    numeros = re.findall(r"\d+", texto)
    return numeros[0] if numeros else np.nan


# --------------------------------------
# Funciones para extraer “listings” (links)
# --------------------------------------
def get_remax_links(max_pages=1, headless=True, driver_path=None):
    browser = create_browser_remax(headless, driver_path)
    links = []
    wait = WebDriverWait(browser, 15)

    for page in range(max_pages):
        url = REMAX_LISTING_URL.format(page=page)
        print(f"[REMAX] Cargando página {page}: {url}")
        browser.get(url)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-remax__container")))
        except:
            print(f"[REMAX] Timeout en página {page}")
            continue

        soup = bs(browser.page_source, 'lxml')
        cards = soup.find_all("div", class_="card-remax__container")
        print(f"[REMAX] Encontradas {len(cards)} propiedades en página {page}")

        for card in cards:
            titulo_tag = card.find("p", class_="card__description")
            link_tag = card.find("a", href=True)
            if titulo_tag and link_tag:
                titulo = safe_find_text(titulo_tag)
                link = REMAX_BASE + link_tag["href"]
                links.append({"Título": titulo, "Link": link})
        time.sleep(random.uniform(1, 2))

    browser.quit()
    df = pd.DataFrame(links)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/links_propiedades_remax.csv", index=False, encoding="utf-8-sig", sep=";")
    print(f"[REMAX] Guardados {len(links)} links en data/links_propiedades_remax.csv")
    return df

def get_zona_links(max_pages=2, headless=False):
    """
    Obtiene los links de ZonaProp; aquí sí usamos undetected_chromedriver.
    """
    browser = create_browser_zona(headless=headless)
    wait = WebDriverWait(browser, 15)
    links = []

    try:
        for page in range(1, max_pages + 1):
            url = ZONA_LISTING_URL.format(page=page)
            print(f"[ZONA] Cargando página {page}: {url}")
            browser.get(url)

            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-to-posting]")))
            except Exception as e:
                print(f"[ZONA] Timeout esperando tarjetas en la página {page}: {e}")
                continue

            html = browser.page_source
            soup = bs(html, "lxml")
            tarjetas = soup.find_all("div", attrs={"data-to-posting": True})
            print(f"[ZONA] Encontradas {len(tarjetas)} propiedades en página {page}")

            for tarjeta in tarjetas:
                link_rel = tarjeta.get("data-to-posting")
                if link_rel:
                    full_link = ZONA_BASE + link_rel
                    links.append({"Link": full_link})

            time.sleep(random.uniform(1, 2))  # pequeño delay para no saturar

    except Exception as e:
        print(f"[ZONA] Error general en el scraping: {e}")

    finally:
        browser.quit()

    df = pd.DataFrame(links)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/links_propiedades_zona.csv", index=False, encoding="utf-8-sig", sep=";")
    print(f"[ZONA] Guardados {len(links)} links en data/links_propiedades_zona.csv")

    return df



# -----------------------------------------
# Funciones adaptadas para extraer detalles
# (reciben browser y wait ya creados)
# -----------------------------------------
def extract_remax_detail(url, headless, driver_path, browser, wait):
    data = {}
    try:
        browser.get(url)
        wait.until(EC.presence_of_element_located((By.ID, "title")))
        wait.until(EC.presence_of_element_located((By.ID, "ubication-text")))

        soup = bs(browser.page_source, 'lxml')

        data["Link"] = url
        data["Título"] = safe_find_text(soup.find("div", id="title"))
        data["Valor Alquiler"] = safe_find_text(soup.find("div", id="price-container"))
        raw_expensas = safe_find_text(soup.find("div", id="expenses-container"))
        data["Expensas"] = raw_expensas.replace("Expensas :", "").strip()

        ubic = soup.find("p", {"id": "ubication-text"})
        loc_text = safe_find_text(ubic)
        data["Dirección"] = loc_text if loc_text else np.nan
        if loc_text and ',' in loc_text:
            partes = [p.strip() for p in loc_text.split(',')]
            data["Barrio"] = partes[-2] if len(partes) >= 2 else np.nan
        else:
            data["Barrio"] = np.nan

        features = {
            "dimensionTotalBuilt": "Metros Cuadrados",
            "totalRooms": "Ambientes",
            "bedrooms": "Dormitorios",
            "bathrooms": "Baños",
            "parkingSpaces": "Cocheras",
            "antiquity": "Años de Antigüedad"
        }
        for info_key, label in features.items():
            div = soup.find("div", {"data-info": info_key, "class": "feature"})
            span = div.find("span", class_="bold") if div else None
            data[label] = safe_find_text(span) if span else np.nan

        desc = safe_find_text(soup.find("h3", id="last"))
        data["Descripción"] = desc

    except Exception as e:
        print(f"[REMAX] Error extrayendo {url}: {e}")

    if "Link" in data:
        link_val = data.pop("Link")
        data["Link"] = link_val

    return data

def extract_zona_detail(url, headless, driver_path, browser, wait):
    data = {}
    try:
        browser.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "section-title")))
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "div.section-location-property.section-location-property-classified"
        )))

        soup = bs(browser.page_source, 'lxml')

        data["Link"] = url
        data["Título"] = safe_find_text(soup.find("div", class_="section-title"))
        data["Valor Alquiler"] = safe_find_text(soup.find("div", class_="price-value"))
        raw_expensas = safe_find_text(soup.find("span", class_="price-expenses"))
        data["Expensas"] = raw_expensas.replace("Expensas:", "").strip()

        ubic_container = soup.find("div", class_="section-location-property section-location-property-classified")
        if ubic_container:
            dir_elem = ubic_container.find("h4")
            loc_text = safe_find_text(dir_elem)
            data["Dirección"] = loc_text if loc_text else np.nan
            if loc_text and ',' in loc_text:
                partes = [p.strip() for p in loc_text.split(',')]
                data["Barrio"] = partes[-2] if len(partes) >= 2 else np.nan
            else:
                data["Barrio"] = np.nan
        else:
            data["Dirección"] = np.nan
            data["Barrio"] = np.nan

        icons = soup.find_all("li", class_="icon-feature")
        features_map = {
            "icon-stotal": "Metros Cuadrados",
            "icon-ambiente": "Ambientes",
            "icon-dormitorio": "Dormitorios",
            "icon-bano": "Baños",
            "icon-cochera": "Cocheras",
            "icon-antiguedad": "Años de Antigüedad"
        }
        for label in features_map.values():
            data[label] = np.nan

        for li in icons:
            icon = li.find("i")
            texto = ' '.join(li.stripped_strings)
            if icon:
                clases = icon.get("class", [])
                for key, label in features_map.items():
                    if key in clases:
                        data[label] = extraer_numero(texto)

        desc = safe_find_text(soup.find("div", id="longDescription"))
        data["Descripción"] = desc

    except Exception as e:
        print(f"[ZONA] Error extrayendo {url}: {e}")

    if "Link" in data:
        link_val = data.pop("Link")
        data["Link"] = link_val

    return data


# -----------------------------------------
# worker_scrape: reutiliza 1 navegador x proceso
# -----------------------------------------
def worker_scrape(urls_chunk, extract_func, headless, driver_path):
    results = []

    # Si es Zonaprop, creamos el navegador con undetected_chromedriver
    if extract_func.__name__ == "extract_zona_detail":
        browser = create_browser_zona(headless=headless)
    else:
        browser = create_browser_remax(headless, driver_path)

    wait = WebDriverWait(browser, 15)

    for url in urls_chunk:
        try:
            data = extract_func(url, headless, driver_path, browser, wait)
            if data:
                results.append(data)
                print(f"[Worker {os.getpid()}] Extraído de {url}")
        except Exception as e:
            print(f"[Worker {os.getpid()}] Error en {url}: {e}")

    browser.quit()
    return results


# -----------------------------------------
# scrape_details_concurrent: reparte URLs en “chunks”
# -----------------------------------------
def scrape_details_concurrent(
        urls,
        extract_func,
        output_csv,
        max_workers=2,
        driver_path=None,
        headless=True
    ):
    """
    Reparte la lista total de URLs en ~max_workers partes, y levanta un proceso por parte.
    Cada proceso corre worker_scrape sobre su trozo, usando 1 navegador para todo ese trozo.
    """
    total = len(urls)
    if total == 0:
        print("No hay URLs para procesar.")
        return pd.DataFrame()

    chunk_size = math.ceil(total / max_workers)
    url_chunks = [urls[i : i + chunk_size] for i in range(0, total, chunk_size)]

    print(f"Dividiendo {total} URLs en {len(url_chunks)} chunks (cada uno ~{chunk_size} URLs).")

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(worker_scrape, chunk, extract_func, headless, driver_path)
            for chunk in url_chunks
        ]
        for future in as_completed(futures):
            parcial = future.result()
            results.extend(parcial)

    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig", sep=";")
    print(f"Guardado detalles en {output_csv} (total {len(results)} registros).")
    return df


# --------------------
# Función MAIN
# --------------------
def main():
    freeze_support()  # Necesario en Windows cuando se usan multiprocessing antes de __main__

    parser = argparse.ArgumentParser(description="Scraper para REMAX y ZonaProp")
    parser.add_argument("--site", choices=["remax", "zona"], required=True,
                        help="Scrapear 'remax' o 'zona'")
    parser.add_argument("--list-only", action="store_true",
                        help="Solo extraer links, no detalles")
    parser.add_argument("--pages", type=int, default=1,
                        help="Cantidad de páginas a scrapear (por defecto: 1 para REMAX, 2 para Zona)")
    parser.add_argument("--workers", type=int, default=4,
                        help="Procesos concurrentes para extraer detalles (por defecto: 4)")
    parser.add_argument("--driver-path", type=str, default=None,
                        help="Ruta al chromedriver.exe (opcional)")
    args = parser.parse_args()

    if args.site == "remax":
        df_links = get_remax_links(max_pages=args.pages, headless=True, driver_path=args.driver_path)
        if args.list_only:
            return
        urls = df_links['Link'].dropna().tolist()
        scrape_details_concurrent(
            urls,
            extract_remax_detail,
            "data/detalles_remax.csv",
            max_workers=args.workers,
            driver_path=args.driver_path,
            headless=True
        )

    elif args.site == "zona":
        # 1) Precargamos el binario antes de lanzar procesos
        preload_driver_binary()

        df_links = get_zona_links(max_pages=args.pages, headless=False)
        if args.list_only:
            return
        urls = df_links['Link'].dropna().tolist()
        scrape_details_concurrent(
            urls,
            extract_zona_detail,
            "data/detalles_zona.csv",
            max_workers=args.workers,
            driver_path=args.driver_path,
            headless=False
        )

if __name__ == "__main__":
    main()
