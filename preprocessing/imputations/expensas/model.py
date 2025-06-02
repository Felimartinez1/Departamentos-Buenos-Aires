from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

def entrenar_modelo(X, y, preprocessor):
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=33)

    pipe = Pipeline([
        ('preprocessing', preprocessor),
        ('regressor', RandomForestRegressor(random_state=42))
    ])

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_val)

    r2 = r2_score(y_val, y_pred)
    mae = mean_absolute_error(y_val, y_pred)

    print(f"R²: {r2:.3f}")
    print(f"MAE: {mae:,.2f}")

    return pipe
