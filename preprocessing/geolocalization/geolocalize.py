import pandas as pd
from .geoconfig import geocode
from .utils import direccion_valida, normalizar_direccion
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_coords(direccion: str, barrio: str) -> pd.Series:
    direccion_valida_resultado = direccion_valida(direccion)

    if direccion_valida_resultado:
        direccion_normalizada = normalizar_direccion(direccion_valida_resultado)

        posibles_direcciones = []
        if isinstance(barrio, str) and barrio.strip():
            posibles_direcciones.append(
                f"{direccion_normalizada}, {barrio.strip()}, Capital Federal, Argentina"
            )
        posibles_direcciones.append(
            f"{direccion_normalizada}, Capital Federal, Argentina"
        )

        for direccion_caba in posibles_direcciones:
            try:
                location = geocode(direccion_caba)
                if location:
                    print(f"Entrada: {direccion_caba} → Geolocalizado como: {location.address}")
                    return pd.Series([location.latitude, location.longitude])
            except (GeocoderTimedOut, GeocoderUnavailable) as e:
                print(f"Timeout para: {direccion_caba} → {e}")
            except Exception as e:
                print(f"Error con {direccion_caba}: {e}")

    return pd.Series([None, None])
