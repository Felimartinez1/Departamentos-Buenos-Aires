import numpy as np
import pandas as pd

# Mapeo de sub-barrios a barrio principal
BARRIOS_EQUIVALENTES = {
    "Palermo Chico": "Palermo",
    "Palermo Soho": "Palermo",
    "Palermo Hollywood": "Palermo",
    "Palermo Viejo": "Palermo",
    "Las Cañitas": "Palermo",
    "Barrio Norte": "Recoleta",
    "Plaza Francia": "Recoleta",
    "Facultad de Derecho": "Recoleta",
    "Catalinas": "Retiro",
    "Microcentro": "San Nicolás",
    "Centro": "San Nicolás",
    "Abasto": "Balvanera",
    "Almagro Norte": "Almagro",
    "Parque Centenario": "Caballito",
    "San Telmo": "San Telmo",
    "Constitución": "Constitución",
    "Belgrano R": "Belgrano",
    "Belgrano C": "Belgrano",
    "Chinatown": "Belgrano",
    "Barrancas de Belgrano": "Belgrano",
    "Barrio Chino": "Belgrano",
    "La Chacarita": "Chacarita",
    "Monserrat": "Montserrat",
    "Puerto Madero": "Puerto Madero",
    "Villa Crespo": "Villa Crespo",
    "Once": "Balvanera",
    "Parque Patricios": "Parque Patricios",
    "Villa General Mitre": "Villa General Mitre",
    "Villa del Parque": "Villa del Parque",
    "Villa Devoto": "Villa Devoto",
    "Villa Urquiza": "Villa Urquiza",
    "Villa Ortúzar": "Villa Ortúzar",
    "Villa Lugano": "Villa Lugano",
    "Villa Luro": "Villa Luro",
    "Villa Pueyrredón": "Villa Pueyrredón",
    "Villa Riachuelo": "Villa Riachuelo",
    "Liniers": "Liniers",
    "Mataderos": "Mataderos",
    "Parque Avellaneda": "Parque Avellaneda",
    "Parque Chacabuco": "Parque Chacabuco",
    "Parque Chas": "Parque Chas",
    "Núñez": "Núñez",
    "Lomas de Núñez": "Núñez",
    "Saavedra": "Saavedra",
    "Coghlan": "Coghlan",
    "Agronomía": "Agronomía",
    "Flores": "Flores",
    "Floresta": "Floresta",
    "Monte Castro": "Monte Castro",
    "Versalles": "Versalles",
    "Vélez Sarsfield": "Vélez Sarsfield",
    "San Cristóbal": "San Cristóbal",
    "Boedo": "Boedo",
    "Pompeya": "Nueva Pompeya",
    "Boedo Norte": "Boedo",
    "Caballito Norte": "Caballito",
    "Caballito Sur": "Caballito",
    "Villa Crespo Norte": "Villa Crespo",
    "Parque Chacabuco Norte": "Parque Chacabuco",
}

def extraer_barrio(ubicacion: str) -> str:
    if not isinstance(ubicacion, str):
        return np.nan

    partes = ubicacion.split(',')
    if len(partes) == 2:
        parte_1 = partes[0].strip()
        parte_2 = partes[1].strip()
        barrio = parte_2 if parte_2 != 'Capital Federal' else parte_1
    else:
        barrio = ubicacion.strip()

    return BARRIOS_EQUIVALENTES.get(barrio, barrio)

def aplicar_extraccion_barrio(df: pd.DataFrame) -> pd.DataFrame:
    df['Barrio Principal'] = df['Barrio'].apply(extraer_barrio)
    return df
