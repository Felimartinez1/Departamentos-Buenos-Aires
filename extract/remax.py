import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

# Iniciar navegador
browser = uc.Chrome()

# Configurar URL base
base_url = "https://www.remax.com.ar/listings"
params = "?region=Capital+Federal&status=ForRent"  # Cambiar a ForRent para alquiler
max_paginas = 10  # Cambiar según necesidad

datos_lista = []

for pagina in range(1, max_paginas + 1):
    print(f"Procesando página {pagina}...")
    url = f"{base_url}{params}&page={pagina}"
    browser.get(url)
    time.sleep(random.uniform(5, 7))

    # Scroll para cargar todos los resultados
    for _ in range(4):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 2))

    # Parsear HTML
    soup = bs(browser.page_source, "lxml")
    propiedades = soup.find_all("div", class_="propertyCardWrapper")

    for prop in propiedades:
        try:
            titulo = prop.find("h2").text.strip()
            ubicacion = prop.find("div", class_="address").text.strip()
            precio = prop.find("div", class_="price").text.strip()
            detalles_raw = prop.find("div", class_="features")
            detalles = detalles_raw.text.strip().replace("\n", " | ") if detalles_raw else "No disponible"
            link = "https://www.remax.com.ar" + prop.find("a")["href"]
            
            datos_lista.append({
                "Título": titulo,
                "Ubicación": ubicacion,
                "Precio": precio,
                "Detalles": detalles,
                "Link": link
            })
        except Exception as e:
            print("Error al extraer una propiedad:", e)
            continue

# Guardar en CSV
df = pd.DataFrame(datos_lista)
df.to_csv("remax_caba_venta.csv", index=False, encoding="utf-8-sig", sep=";")

print("✅ Datos extraídos con éxito.")
browser.quit()
