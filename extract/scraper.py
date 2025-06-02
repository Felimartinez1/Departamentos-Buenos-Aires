import time
import argparse
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
    parser.add_argument("--pages", type=int, default=None,
                        help="Cantidad de páginas a scrapear (por defecto: todas)")
    parser.add_argument("--workers", type=int, default=4,
                        help="Procesos concurrentes para extraer detalles (por defecto: 4)")
    parser.add_argument("--driver-path", type=str, default=None,
                        help="Ruta al chromedriver.exe (opcional)")
    args = parser.parse_args()

    if args.site == "remax":
        df_links = get_remax_links(max_pages=args.pages, headless=False, driver_path=args.driver_path)
        if args.list_only:
            return
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

        df_links = get_zona_links(max_pages=args.pages, headless=False)
        if args.list_only:
            return
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
