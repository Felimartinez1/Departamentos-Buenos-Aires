import requests
from bs4 import BeautifulSoup as bs
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc


browser = uc.Chrome()


base_url = "https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-pagina-{}.html"
max_paginas = 791
x = 1
links_lista = []

try:
    while x <= max_paginas:
        url = base_url.format(x)
        print(f"Extrayendo página {x}: {url}")
        
        browser.get(url)
        time.sleep(random.uniform(7, 10))

        body = browser.find_element("tag name", "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(2, 4))

        html = browser.page_source
        soup = bs(html, "lxml")

        
        tarjetas = soup.find_all("div", attrs={"data-to-posting": True})
        print(f"Links encontrados en página {x}: {len(tarjetas)}")

        for tarjeta in tarjetas:
            link_relativo = tarjeta.get("data-to-posting")
            if link_relativo:
                link = "https://www.zonaprop.com.ar" + link_relativo
                links_lista.append({"Link": link})

        
        df = pd.DataFrame(links_lista)
        df.to_csv("LinksPropiedades_Zona.csv", index=False, encoding="utf-8-sig", sep=";")
        print(f"Página {x} guardada correctamente. Total links hasta ahora: {len(links_lista)}\n")

        x += 1

except Exception as e:
    print(f"Se produjo un error o se cerró el navegador: {e}")

finally:
    
    if links_lista:
        df = pd.DataFrame(links_lista)
        df.to_csv("links_propiedades_zona.csv", index=False, encoding="utf-8-sig", sep=";")
        print(f"\nCSV actualizado con {len(links_lista)} links.")

    
    try:
        browser.quit()
    except:
        pass
