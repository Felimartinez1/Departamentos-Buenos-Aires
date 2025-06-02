import os
import time
import random
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from constants import ZONA_LISTING_URL, ZONA_BASE
from utils import safe_find_text, extraer_numero, parse_html
from browsers import create_browser_zona

def get_zona_links(max_pages: int = None, headless: bool = False) -> pd.DataFrame:
    """
    Recorre todas las páginas de ZonaProp (o hasta max_pages) y devuelve
    un DataFrame con la columna 'Link'. Guarda CSV en data/links_propiedades_zona.csv.
    """
    browser = create_browser_zona(headless=headless)
    wait = WebDriverWait(browser, 15)
    links = []
    page = 1

    try:
        while True:
            if max_pages and page > max_pages:
                break

            url = ZONA_LISTING_URL.format(page=page)
            print(f"[ZONA] Cargando página {page}: {url}")
            browser.get(url)

            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-to-posting]")))
            except Exception as e:
                print(f"[ZONA] Timeout esperando tarjetas en la página {page}: {e}")
                break

            soup = parse_html(browser.page_source)
            tarjetas = soup.find_all("div", attrs={"data-to-posting": True})
            print(f"[ZONA] Encontradas {len(tarjetas)} propiedades en página {page}")

            if not tarjetas:
                break

            for tarjeta in tarjetas:
                link_rel = tarjeta.get("data-to-posting")
                if link_rel:
                    full_link = ZONA_BASE + link_rel
                    links.append({"Link": full_link})

            page += 1
            time.sleep(random.uniform(1, 2))

    except Exception as e:
        print(f"[ZONA] Error general en el scraping: {e}")
    finally:
        browser.quit()

    df = pd.DataFrame(links)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/links_propiedades_zona.csv", index=False, encoding="utf-8-sig", sep=";")
    print(f"[ZONA] Guardados {len(links)} links en data/links_propiedades_zona.csv")
    return df

def extract_zona_detail(url: str, browser, wait) -> dict:
    """
    Extrae detalles de una propiedad de ZonaProp dado su URL. Recibe
    un browser undetected_chromedriver ya inicializado y un WebDriverWait (15s).
    Devuelve un dict con las claves definidas en el script original.
    """
    data = {}
    try:
        browser.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "section-title")))
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "div.section-location-property.section-location-property-classified"
        )))

        soup = parse_html(browser.page_source)
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
            if loc_text and "," in loc_text:
                partes = [p.strip() for p in loc_text.split(",")]
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
        # Inicializar todas las keys en np.nan
        for label in features_map.values():
            data[label] = np.nan

        for li in icons:
            icon = li.find("i")
            texto = " ".join(li.stripped_strings)
            if icon:
                clases = icon.get("class", [])
                for key, label in features_map.items():
                    if key in clases:
                        data[label] = extraer_numero(texto)

        desc = safe_find_text(soup.find("div", id="longDescription"))
        data["Descripción"] = desc

    except Exception as e:
        print(f"[ZONA] Error extrayendo {url}: {e}")

    return data
