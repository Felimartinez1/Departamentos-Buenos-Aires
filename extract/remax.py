import os
import time
import random
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from constants import REMAX_LISTING_URL, REMAX_BASE
from utils import safe_find_text, parse_html
from browsers import create_browser_remax

def get_remax_links(max_pages: int = None, headless: bool = True, driver_path: str = None) -> pd.DataFrame:
    """
    Recorre todas las páginas (o hasta max_pages, si se especifica)
    y extrae los links de cada tarjeta de REMAX.
    Guarda el CSV en data/links_propiedades_remax.csv y devuelve el DataFrame.
    """
    browser = create_browser_remax(headless, driver_path)
    links = []
    wait = WebDriverWait(browser, 15)
    page = 0

    while True:
        url = REMAX_LISTING_URL.format(page=page)
        print(f"[REMAX] Cargando página {page}: {url}")
        browser.get(url)

        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-remax__container")))
        except:
            print(f"[REMAX] Timeout en página {page} — posible fin de resultados.")
            break

        soup = parse_html(browser.page_source)
        cards = soup.find_all("div", class_="card-remax__container")
        print(f"[REMAX] Encontradas {len(cards)} propiedades en página {page}")

        if not cards:
            break

        for card in cards:
            titulo_tag = card.find("p", class_="card__description")
            link_tag = card.find("a", href=True)
            if titulo_tag and link_tag:
                titulo = safe_find_text(titulo_tag)
                link = REMAX_BASE + link_tag["href"]
                links.append({"Título": titulo, "Link": link})

        page += 1
        if max_pages is not None and page >= max_pages:
            print(f"[REMAX] Alcanzado max_pages={max_pages}, deteniendo.")
            break

        time.sleep(random.uniform(1, 2))

    browser.quit()

    df = pd.DataFrame(links)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/links_propiedades_remax.csv", index=False, encoding="utf-8-sig", sep=";")
    print(f"[REMAX] Guardados {len(links)} links en data/links_propiedades_remax.csv")
    return df

def extract_remax_detail(url: str, browser, wait) -> dict:
    """
    Extrae detalles de una propiedad de REMAX dado su URL. Debe recibir
    un browser Selenium ya inicializado y un WebDriverWait (15s).
    Devuelve un dict con las claves definidas en el script original.
    """
    data = {}
    try:
        browser.get(url)
        wait.until(EC.presence_of_element_located((By.ID, "title")))
        wait.until(EC.presence_of_element_located((By.ID, "ubication-text")))

        soup = parse_html(browser.page_source)

        data["Link"] = url
        data["Título"] = safe_find_text(soup.find("div", id="title"))
        data["Valor Alquiler"] = safe_find_text(soup.find("div", id="price-container"))
        raw_expensas = safe_find_text(soup.find("div", id="expenses-container"))
        data["Expensas"] = raw_expensas.replace("Expensas :", "").strip()

        ubic = soup.find("p", {"id": "ubication-text"})
        loc_text = safe_find_text(ubic)
        data["Dirección"] = loc_text if loc_text else np.nan
        if loc_text and "," in loc_text:
            partes = [p.strip() for p in loc_text.split(",")]
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

    return data
