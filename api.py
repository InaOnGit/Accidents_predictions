from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI(title = "API Prédiction Accidents")

model = joblib.load('model_logistic_regression.pkl')
columns = joblib.load('model_columns.pkl')

@app.get("/")
def home(): 
    return{"message": "API marche", "status" : "OK"}

@app.get("/health")
def health():
    return{"status": "healthy", "model": "Logistic Regression"}

@app.post("/predict")
def predict(heure: int = 14, lum: int = 1, atm: int = 1, age: float = 30, 
            catr: int = 3, agg: int = 2, sexe: int = 1, catv: int = 7):

    data = {col: 0 for col in columns} #le dictionnaire avec les colonnes vides à 0
    
#on rajoute les vealurs dans le dictionnaire
    data['heure'] = heure
    data['lum'] = lum
    data['atm'] = atm
    data['age'] = age
    data['catr'] = catr
    data['agg'] = agg
    data['sexe'] = sexe
    data['catv'] = catv
    
#on calcule les features supplem. 
    data['nuit'] = 1 if (heure >= 22 or heure <= 6) else 0
    data['jeune_conducteur'] = 1 if age < 25 else 0
    data['conditions_dangereuses'] = 1 if (atm in [2,3,4,5,6] or lum in [3,4]) else 0
    
#on crée une df 
    df = pd.DataFrame([data])[columns]
    
#le prédiction 
    prediction = int(model.predict(df)[0])
    proba = model.predict_proba(df)[0]
    
    return {
        "gravite": "Grave" if prediction == 1 else "Non grave",
        "probabilite_grave": round(float(proba[1]) * 100, 1),
        "probabilite_non_grave": round(float(proba[0]) * 100, 1)
    }
