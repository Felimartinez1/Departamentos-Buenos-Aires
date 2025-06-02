import numpy as np
from sklearn.impute import KNNImputer
import pandas as pd

def imputar_cero_cocheras_dormitorios(df: pd.DataFrame) -> pd.DataFrame:
    df['Cocheras'] = df['Cocheras'].fillna(0)
    df['Dormitorios'] = df['Dormitorios'].fillna(0)
    return df

def imputar_baños(df: pd.DataFrame) -> pd.DataFrame:
    # Reemplaza 0 por NaN para imputar baños
    df['Baños'] = df['Baños'].replace(0, np.nan)
    imputer = KNNImputer(n_neighbors=5)
    columnas_para = [
        'Baños', 'Ambientes', 'Metros Cuadrados',
        'Dormitorios', 'Valor Alquiler(normalizado)'
    ]
    # Ejecuta la imputación
    resultado = imputer.fit_transform(df[columnas_para])
    df['Baños'] = np.round(resultado[:, 0]).astype(int)
    return df

def imputar_antiguedad(df: pd.DataFrame) -> pd.DataFrame:
    # Reemplaza 0 por NaN para imputar antigüedad
    df['Años de Antigüedad'] = df['Años de Antigüedad'].replace(0, np.nan)
    imputer = KNNImputer(n_neighbors=5)
    columnas_para = [
        'Años de Antigüedad', 'Ambientes', 'Metros Cuadrados',
        'Dormitorios', 'Valor Alquiler(normalizado)'
    ]
    resultado = imputer.fit_transform(df[columnas_para])
    df['Años de Antigüedad'] = np.round(resultado[:, 0]).astype(int)
    return df

def imputar_expensas(df: pd.DataFrame, modelo, features: list) -> pd.DataFrame:
    es_nulo = df['Expensas'].isnull()
    X_null = df.loc[es_nulo, features]
    
    predicciones = modelo.predict(X_null)

    df.loc[es_nulo, 'Expensas'] = predicciones
    df['Expensas'] = df['Expensas'].astype(float).round(0).astype(int)
    df['Expensas Predichas'] = 0
    df.loc[es_nulo, 'Expensas Predichas'] = 1

    return df
