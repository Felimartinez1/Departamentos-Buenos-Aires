import os
import time
import argparse
import pandas as pd
from multiprocessing import freeze_support

from constants import REMAX_BASE, ZONA_BASE
from remax import get_remax_links
from zona import get_zona_links
from worker import scrape_details_concurrent
from browsers import preload_driver_binary

def main():
    freeze_support()  # Necesario en Windows cuando se usan ProcessPoolExecutor

    parser = argparse.ArgumentParser(description="Scraper para REMAX y ZonaProp")
    parser.add_argument("--site", choices=["remax", "zona"], required=True,
                        help="Scrapear 'remax' o 'zona'")
    parser.add_argument("--list-only", action="store_true",
                        help="Solo extraer links, no detalles")
    parser.add_argument("--details-only", action="store_true",
                        help="Solo extraer detalles a partir del CSV de links ya existente")
    parser.add_argument("--pages", type=int, default=None,
                        help="Cantidad de páginas a scrapear (por defecto: todas)")
    parser.add_argument("--workers", type=int, default=4,
                        help="Procesos concurrentes para extraer detalles (por defecto: 4)")
    parser.add_argument("--driver-path", type=str, default=None,
                        help="Ruta al chromedriver.exe (opcional)")
    args = parser.parse_args()

    # Ruta de los archivos de links preexistentes
    remax_links_csv = "data/links_propiedades_remax.csv"
    zona_links_csv = "data/links_propiedades_zona.csv"

    # Si piden solo detalles, verificamos que exista el CSV correspondiente
    if args.details_only:
        if args.site == "remax":
            if not os.path.isfile(remax_links_csv):
                print(f"[ERROR] No existe el archivo de links de REMAX: {remax_links_csv}")
                return
            df_links = pd.read_csv(remax_links_csv, sep=";")
            urls = df_links["Link"].dropna().tolist()
            print(f"[REMAX] Cargando {len(urls)} URLs desde {remax_links_csv} para extraer detalles.")
            scrape_details_concurrent(
                urls=urls,
                site="remax",
                output_csv="data/detalles_remax.csv",
                max_workers=args.workers,
                driver_path=args.driver_path,
                headless=False
            )
            return

        elif args.site == "zona":
            if not os.path.isfile(zona_links_csv):
                print(f"[ERROR] No existe el archivo de links de ZonaProp: {zona_links_csv}")
                return
            df_links = pd.read_csv(zona_links_csv, sep=";")
            urls = df_links["Link"].dropna().tolist()
            print(f"[ZONA] Cargando {len(urls)} URLs desde {zona_links_csv} para extraer detalles.")
            start_time = time.time()
            scrape_details_concurrent(
                urls=urls,
                site="zona",
                output_csv="data/detalles_zona.csv",
                max_workers=args.workers,
                driver_path=args.driver_path,
                headless=False
            )
            elapsed = time.time() - start_time
            print(f"[ZONA] Tiempo total scrape_details_concurrent: {elapsed:.2f} segundos")
            return

    # Si piden solo la lista de links (no detalles), ejecutamos get_*_links y salimos:
    if args.list_only:
        if args.site == "remax":
            get_remax_links(max_pages=args.pages, headless=False, driver_path=args.driver_path)
        elif args.site == "zona":
            preload_driver_binary()
            get_zona_links(max_pages=args.pages, headless=False)
        return

    # Caso normal: extraemos links y luego inmediatamente detalles
    if args.site == "remax":
        # 1) Extraer links
        df_links = get_remax_links(max_pages=args.pages, headless=False, driver_path=args.driver_path)
        # 2) Extraer detalles
        urls = df_links["Link"].dropna().tolist()
        scrape_details_concurrent(
            urls=urls,
            site="remax",
            output_csv="data/detalles_remax.csv",
            max_workers=args.workers,
            driver_path=args.driver_path,
            headless=False
        )

    elif args.site == "zona":
        # Precarga binario de undetected-chromedriver para evitar colisiones
        preload_driver_binary()
        # 1) Extraer links
        df_links = get_zona_links(max_pages=args.pages, headless=False)
        # 2) Extraer detalles
        urls = df_links["Link"].dropna().tolist()
        start_time = time.time()
        scrape_details_concurrent(
            urls=urls,
            site="zona",
            output_csv="data/detalles_zona.csv",
            max_workers=args.workers,
            driver_path=args.driver_path,  # no se usa en zona, pero lo incluimos para la firma
            headless=False
        )
        elapsed = time.time() - start_time
        print(f"[ZONA] Tiempo total scrape_details_concurrent: {elapsed:.2f} segundos")

if __name__ == "__main__":
    main()
