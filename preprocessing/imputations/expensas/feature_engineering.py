import pandas as pd

def preparar_df_model(df: pd.DataFrame) -> pd.DataFrame:
    df_viejo = pd.read_csv('C:/Users/Felipe/OneDrive/Escritorio/Mini Projects/Departamentos Buenos Aires/data/clean_Alquileres.csv') ### data vieja
    df_viejo = df_viejo[df_viejo['Expensas Predichas'] == 0]
    df_viejo.rename(columns={'Barrio': 'Barrio Principal'}, inplace=True)

    df_model = df.dropna(subset=['Expensas'])
    df_model = df_model[['Valor Alquiler(normalizado)', 'Barrio Principal', 'Dormitorios', 'Moneda', 'Cocheras', 'Ambientes', 'Baños', 'Metros Cuadrados', 'Expensas']]

    # Preparar df_viejo con mismas columnas que df_model
    df_viejo = df_viejo[['Valor Alquiler(normalizado)', 'Barrio Principal', 'Dormitorios', 'Moneda', 'Cocheras', 'Ambientes', 'Baños', 'Metros Cuadrados', 'Expensas']]

    # Unir ambos
    df_model = pd.concat([df_model, df_viejo], ignore_index=True)

    df_model['Expensas'] = df_model['Expensas'].astype(int)

    df_model = df_model[(df_model['Expensas'] >= 25000) & (df_model['Expensas'] <= 1300000)].reset_index(drop=True)
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
