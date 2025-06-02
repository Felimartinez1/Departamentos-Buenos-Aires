import re
import numpy as np
from bs4 import BeautifulSoup as bs

def safe_find_text(soup_elem):
    """Devuelve el texto limpio de un elemento BeautifulSoup, o cadena vacía si es None."""
    return soup_elem.get_text(strip=True) if soup_elem else ""

def extraer_numero(texto: str):
    """
    Dado un texto, extrae la primera aparición de dígitos (p. ej. "72 m²" → "72").
    Devuelve np.nan si no hay números.
    """
    if not texto:
        return np.nan
    numeros = re.findall(r"\d+", texto)
    return numeros[0] if numeros else np.nan

def parse_html(html: str):
    """Crea y devuelve un objeto BeautifulSoup con parser 'lxml'."""
    return bs(html, "lxml")
