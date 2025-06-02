import numpy as np
import pandas as pd

# Importar todos los módulos que contienen las funciones
from load_data import load_dataset
from initial_filters import filtrar_datos_iniciales

from imputations.expensas.feature_engineering import preparar_df_model, obtener_features_target
from imputations.expensas.pipeline import construir_preprocessor
from imputations.expensas.model import entrenar_modelo
from imputations.imputations import (
    imputar_cero_cocheras_dormitorios,
    imputar_baños,
    imputar_antiguedad,
    imputar_expensas
)

from normalization import (
    normalizar_moneda_y_valor,
    limpiar_expensas,
    eliminar_outliers_alquiler,
    filtrar_ambientes_y_dormitorios,
    normalizar_valor_y_filtrar
)

from detection import detectar_amoblado_df
from barrio import aplicar_extraccion_barrio
from conversion import convertir_a_enteros




def limpiar_df() -> pd.DataFrame:
    # Cargar y unificar datasets
    df = load_dataset()

    # Reemplazar cadenas vacías por NaN
    df.replace('', np.nan, inplace=True)

    # Filtros iniciales
    df = filtrar_datos_iniciales(df)

    # Imputación de cero en Cocheras y Dormitorios
    df = imputar_cero_cocheras_dormitorios(df)

    # Normalizar Moneda y Valor
    df = normalizar_moneda_y_valor(df)

    # Limpiar Expensas
    df = limpiar_expensas(df)

    # Eliminar outliers de alquiler
    df = eliminar_outliers_alquiler(df)

    # Filtrar por Ambientes y Dormitorios
    df = filtrar_ambientes_y_dormitorios(df)

    # Normalizar Valor (a ARS) y filtrar rango
    df = normalizar_valor_y_filtrar(df)

    # Imputar Baños (dos veces a propósito, como en el script original)
    df = imputar_baños(df)
    df = imputar_baños(df)

    # Imputar Antigüedad
    df = imputar_antiguedad(df)

    #  Detectar Amoblado
    df = detectar_amoblado_df(df)

    # Extraer Barrio Principal
    df = aplicar_extraccion_barrio(df)
    

    # Preparar df_model
    df_model = preparar_df_model(df)

    # Obtener X, y
    X, y = obtener_features_target(df_model)

    # Preprocessor y entrenamiento
    preprocessor = construir_preprocessor()
    modelo = entrenar_modelo(X, y, preprocessor)

    # Imputar los valores faltantes en el df original
    df = imputar_expensas(df, modelo, X.columns.tolist())


    # Convertir columnas numéricas a enteros
    df = convertir_a_enteros(df)

    # Eliminar duplicados
    cols_clave = [
        'Valor Alquiler(normalizado)',
        'Barrio Principal',
        'Dirección',
        'Dormitorios',
        'Ambientes',
        'Baños',
        'Metros Cuadrados',
        'Descripción'
    ]
    df.drop_duplicates(subset=cols_clave, inplace=True, keep='first')
    
    # Filtrar Expensas
    df = df[(df['Expensas'] >= 25000) & (df['Expensas'] <= 2000000)].reset_index(drop=True)
    
    # Agregar Ids
    df['Id'] = range(1, len(df) + 1)
    
    return df

if __name__ == "__main__":
    df = limpiar_df()
    df.to_csv('data/cleaned_data.csv', index=False)
