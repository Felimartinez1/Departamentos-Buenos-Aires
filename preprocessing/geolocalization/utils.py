import re

def direccion_valida(direccion: str) -> str | None:
    if not isinstance(direccion, str):
        return None

    direccion = direccion.strip()
    direccion = re.sub(r'\bal\b', '', direccion, flags=re.IGNORECASE)

    match = re.search(r'\b([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.]+)\s(\d{2,5})\b', direccion)
    if match:
        calle, altura = match.groups()
        return f"{calle.strip()} {altura}"
    return None

def normalizar_direccion(direccion: str) -> str:
    direccion = re.sub(r'\bal\b', '', direccion, flags=re.IGNORECASE)
    direccion = re.sub(r'\s+', ' ', direccion)
    return direccion.strip()
