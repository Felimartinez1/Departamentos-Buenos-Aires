import pandas as pd

def load_datasets():
    df_zona = pd.read_csv(
        'C:/Users/Felipe/OneDrive/Escritorio/Mini Projects/Departamentos Buenos Aires/data/detalles_zona.csv',
        sep=';',
        encoding='utf-8-sig'
    )
    df_remax = pd.read_csv(
        'C:/Users/Felipe/OneDrive/Escritorio/Mini Projects/Departamentos Buenos Aires/data/detalles_remax.csv',
        sep=';',
        encoding='utf-8-sig'
    )
    df_train = pd.read_csv(
        'C:/Users/Felipe/OneDrive/Escritorio/Mini Projects/Departamentos Buenos Aires/data/clean_Alquileres.csv',
    )
    df_train = df_train[df_train['Expensas Predichas'] == 0]
    df_train = df_train.rename(columns={'Barrio': 'Barrio Principal'})
    
    df_remax['Plataforma'] = 'Remax'
    df_zona['Plataforma'] = 'ZonaProp'

    df = pd.concat([df_remax, df_zona], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df, df_train
