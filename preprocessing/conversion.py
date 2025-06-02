import pandas as pd

def convertir_a_enteros(df: pd.DataFrame) -> pd.DataFrame:
    columnas_a_convertir = [
        'Expensas', 'Ambientes', 'Dormitorios',
        'Años de Antigüedad', 'Cocheras', 'Metros Cuadrados'
    ]
    for col in columnas_a_convertir:
        if col in df.columns:
            df[col] = df[col].round().astype('Int64')
    return df
