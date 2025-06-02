import re
import numpy as np
import pandas as pd
import requests

def normalizar_moneda_y_valor(df: pd.DataFrame) -> pd.DataFrame:
    # Extrae la moneda de la cadena (USD, ARS o $)
    df['Moneda'] = df['Valor Alquiler'].str.extract(r'(USD|\$|ARS)', expand=False)
    df['Moneda'] = df['Moneda'].replace({'$': 'ARS', 'USD': 'USD', 'ARS': 'ARS'})

    # Extrae solo la parte numérica y convierte a entero
    df['Valor Alquiler'] = df['Valor Alquiler'].str.extract(r'([\d\.]+)', expand=False)
    df['Valor Alquiler'] = df['Valor Alquiler'].str.replace('.', '', regex=False)
    df['Valor Alquiler'] = pd.to_numeric(df['Valor Alquiler'], errors='coerce').astype('Int64')

    return df

def limpiar_expensas(df: pd.DataFrame) -> pd.DataFrame:
    # Extrae la parte numérica de Expensas y convierte a float
    df['Expensas'] = df['Expensas'].str.extract(r'([\d\.]+)', expand=False)
    df['Expensas'] = df['Expensas'].str.replace('.', '', regex=False)
    df['Expensas'] = pd.to_numeric(df['Expensas'], errors='coerce')
    return df

def eliminar_outliers_alquiler(df: pd.DataFrame) -> pd.DataFrame:
    filtro_usd = ~((df['Moneda'] == 'USD') & (df['Valor Alquiler'] > 31000))
    filtro_ars = ~(
        (df['Moneda'] == 'ARS') &
        ((df['Valor Alquiler'] < 90000) | (df['Valor Alquiler'] > 42000000))
    )
    df = df[filtro_usd & filtro_ars]
    return df.reset_index(drop=True)

def filtrar_ambientes_y_dormitorios(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(df['Ambientes'] >= 1) & (df['Ambientes'] <= 10)]
    # Si Dormitorios == 0, entonces Ambientes debe ser 1
    df = df[~((df['Dormitorios'] == 0) & (df['Ambientes'] > 1))]
    return df.reset_index(drop=True)

def obtener_dolar_oficial() -> float:
    respuesta = requests.get("https://dolarapi.com/v1/dolares/oficial")
    if respuesta.status_code == 200:
        return respuesta.json()['venta']
    else:
        raise Exception("No se pudo obtener la cotización del dólar")

def normalizar_valor_y_filtrar(df: pd.DataFrame) -> pd.DataFrame:
    cotizacion = obtener_dolar_oficial()
    df['Valor Alquiler(normalizado)'] = np.where(
        df['Moneda'] == 'USD',
        df['Valor Alquiler'] * cotizacion,
        df['Valor Alquiler']
    )
    # Filtrar rango normalizado
    df = df[
        (df['Valor Alquiler(normalizado)'] > 90000) &
        (df['Valor Alquiler(normalizado)'] < 42_000_000)
    ]
    return df.reset_index(drop=True)
