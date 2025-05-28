import requests
from bs4 import BeautifulSoup as bs
import random
import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import re


browser = uc.Chrome()


url = "https://www.remax.com.ar/listings/rent?page=0&pageSize=24&sort=-createdAt&in:operationId=2&in:eStageId=0,1,2,3,4&in:typeId=1,2,3,4,5,6,7,8&locations=in:CF@%3Cb%3ECapital%3C%2Fb%3E%20%3Cb%3EFederal%3C%2Fb%3E::::::&landingPath=&filterCount=1&viewMode=listViewMode"
max_paginas = 1
x = 0

links_lista = []

def limpiar_titulo_para_link(titulo):
    titulo = titulo.lower()
    titulo = re.sub(r"[^\w\s-]", "", titulo)  
    titulo = re.sub(r"\s+", "-", titulo.strip()) 
    return titulo


while x <= max_paginas:

    
    if x == max_paginas:
        print("Se alcanzó la última página, finalizando ejecución.")
        break

    url = f"https://www.remax.com.ar/listings/rent?page={x}&pageSize=24&sort=-createdAt&in:operationId=2&in:eStageId=0,1,2,3,4&in:typeId=1,2,3,4,5,6,7,8&locations=in:CF@%3Cb%3ECapital%3C%2Fb%3E%20%3Cb%3EFederal%3C%2Fb%3E::::::&landingPath=&filterCount=1&viewMode=listViewMode"
    
    browser.get(url)

    time.sleep(random.uniform(8, 11)) 
        
    body = browser.find_element("tag name", "body")
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(random.randint(2, 4)) 

    
    html = browser.page_source
    soup = bs(html, 'lxml')

    
    pagina_texto = soup.find("p", class_="number flex-center-center selected").get_text(strip=True)
    pagina_actual = int(pagina_texto) - 1


    
    if x == pagina_actual:

        
        propiedades = soup.find_all("div", class_="card-remax__container")

        
        for propiedad in propiedades:
            titulo_tag = propiedad.find("p", class_="card__description")
            link_tag = propiedad.find("a", href=True)
            
            if titulo_tag and link_tag:
                titulo = titulo_tag.get_text(strip=True)
                link = "https://www.remax.com.ar" + link_tag["href"]
                links_lista.append({
                    "Titulo": titulo,
                    "Link": link
                })

       
        x = x + 1        
    else:
        
        x = x + 1


df = pd.DataFrame(links_lista)
df.to_csv("links_propiedades_remax.csv", index=False, encoding="utf-8-sig", sep=";")


print("Títulos y links generados correctamente.")
browser.quit()
