import pandas as pd

def filtrar_datos_iniciales(df: pd.DataFrame) -> pd.DataFrame:
    # Filtrar filas con Título y Barrio no vacíos
    df = df[df['Título'].notna() & (df['Título'].str.strip() != '')]
    df = df[df['Barrio'].notna() & (df['Barrio'].str.strip() != '')]

    # Filtrar rango de Metros Cuadrados
    df = df[(df['Metros Cuadrados'] >= 15) & (df['Metros Cuadrados'] <= 1000)]
    df = df.dropna(subset=['Descripción'])
    df.drop_duplicates()


    # Máscaras para asegurar formato adecuado de Valor Alquiler por plataforma
    zonaprop_mask = (
        (df['Plataforma'] == 'ZonaProp') &
        df['Valor Alquiler'].str.contains(r'alquiler\s*(usd|\$)', case=False, na=False)
    )
    remax_mask = (
        (df['Plataforma'] == 'Remax') &
        df['Valor Alquiler'].str.contains(r'(\d[\d\.]*\s*(ARS|USD))', na=False)
    )

    df = df[zonaprop_mask | remax_mask]
    return df.reset_index(drop=True)
