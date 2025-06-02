import os
import math
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from selenium.webdriver.support.ui import WebDriverWait

from browsers import create_browser_remax, create_browser_zona
from remax import extract_remax_detail
from zona import extract_zona_detail

def worker_scrape(urls_chunk, site: str, driver_path: str, headless: bool):
    """
    Cada worker abre un solo navegador y recorre su lista de URLs.
    site: "remax" o "zona"
    Se asume que urls_chunk es lista de strings (urls).
    Devuelve lista de dicts con los datos extraídos.
    """
    results = []

    if site == "zona":
        browser = create_browser_zona(headless=headless)
        extract_func = extract_zona_detail
    else:
        browser = create_browser_remax(headless=headless, driver_path=driver_path)
        extract_func = extract_remax_detail

    wait = WebDriverWait(browser, 15)

    for url in urls_chunk:
        try:
            data = extract_func(url, browser, wait)
            if data:
                results.append(data)
                print(f"[Worker {os.getpid()}] Extraído de {url}")
        except Exception as e:
            print(f"[Worker {os.getpid()}] Error en {url}: {e}")

    browser.quit()
    return results

def scrape_details_concurrent(urls, site: str, output_csv: str, max_workers: int = 2, driver_path: str = None, headless: bool = False) -> pd.DataFrame:
    """
    Divide la lista total de URLs en ~max_workers chunks y levanta un proceso por chunk.
    Cada proceso corre worker_scrape sobre su subconjunto, usando un solo navegador.
    Al final:

    - Combina todos los resultados en un DataFrame.
    - Guarda CSV en output_csv.
    - Devuelve el DataFrame.
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
            executor.submit(worker_scrape, chunk, site, driver_path, headless)
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
