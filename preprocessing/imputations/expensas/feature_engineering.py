import pandas as pd

def preparar_df_model(df: pd.DataFrame) -> pd.DataFrame:
    df_model = df[df['Expensas'].notnull()].copy()
    df_model['Expensas'] = df_model['Expensas'].astype(int)
    df_model = df_model[(df_model['Expensas'] >= 25000) & (df_model['Expensas'] <= 1300000)]
    df_model = df_model.reset_index(drop=True)

    # Agrupamiento de barrios poco frecuentes
    barrio_counts = df_model['Barrio Principal'].value_counts()
    barrio_frecuentes = barrio_counts[barrio_counts >= 60].index
    df_model['Barrio Principal'] = df_model['Barrio Principal'].apply(lambda x: x if x in barrio_frecuentes else 'Otros')

    return df_model


def obtener_features_target(df_model: pd.DataFrame):
    features = ['Ambientes', 'Dormitorios', 'Baños', 'Cocheras', 'Barrio Principal', 'Moneda', 'Metros Cuadrados', 'Valor Alquiler(normalizado)']
    target = 'Expensas'
    X = df_model[features]
    y = df_model[target]
    return X, y
