import re
import string
import numpy as np
import pandas as pd

# Regex para detección de palabras relacionadas con muebles
regex_negativos = [
    r"sin\s+muebles", r"no\s+amoblado", r"sin\s+amoblar", r"no\s+amueblado",
    r"no\s+equipado", r"no\s+tiene\s+muebles", r"no\s+contiene\s+muebles",
    r"no\s+incluye\s+muebles", r"no\s+incluye\s+amoblamiento",
    r"no\s+incluye\s+equipamiento", r"no\s+amoblamiento", r"no\s+equipamiento",
    r"sin\s+amoblamiento", r"sin\s+amueblamiento",
]

regex_positivos = [
    r"amoblado", r"amueblado", r"amoblamientos", r"amoblamiento",
    r"con\s+muebles", r"totalmente\s+equipado", r"full\s+equipado",
    r"\bmuebles\b", r"mobiliario\s+incluido",
]

contextos_que_no_cuentan = [
    r"muebles\s+(inferiores|superiores|de cocina|de baño|de guardado|bajo\s+mesada)",
    r"mueble\s+(adicional|de guardado|bajo\s+mesada|en\s+baño)",
    r"\bplacard\b", r"\balacena\b", r"mueble\s+fijo",
]

def hay_muebles_en_contexto(texto: str, palabra_base="mueble", contextos=None, ventana=8) -> bool:
    if contextos is None:
        contextos = ["cocina", "baño", "mesada", "guardado"]
    palabras = texto.split()
    for i, palabra in enumerate(palabras):
        if palabra_base in palabra:
            contexto = palabras[max(i - ventana, 0): min(i + ventana + 1, len(palabras))]
            if any(ctx in contexto for ctx in contextos):
                return True
    return False

def limpiar_puntuacion(texto: str) -> str:
    return texto.translate(str.maketrans('', '', string.punctuation))

def detectar_amoblado(titulo: str, descripcion: str) -> int:
    texto = f"{titulo} {descripcion}".lower()
    texto = limpiar_puntuacion(texto)

    # Caso especial "con o sin muebles"
    if "con o sin muebles" in texto:
        return 1

    # Si la palabra "muebles" aparece en contexto de cocina/baño/etc., se ignora esa ocurrencia
    if hay_muebles_en_contexto(texto):
        texto = texto.replace("muebles", "").replace("mueble", "")

    # Eliminar patrones que no cuentan como mobiliario completo
    for patron in contextos_que_no_cuentan:
        texto = re.sub(patron, "", texto)

    # Búsqueda de expresiones negativas
    for patron_neg in regex_negativos:
        if re.search(patron_neg, texto):
            return 0

    # Búsqueda de expresiones positivas
    for patron_pos in regex_positivos:
        if re.search(patron_pos, texto):
            return 1

    return 0

def detectar_amoblado_df(df: pd.DataFrame) -> pd.DataFrame:
    df["Amoblado"] = df.apply(
        lambda row: detectar_amoblado(row["Título"], row["Descripción"]),
        axis=1
    )
    return df
