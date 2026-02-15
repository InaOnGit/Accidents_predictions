# Problèmes de Qualité Détectés dans le projet "Accidents"
**Analysé avec :** Ruff, Mypy
 
---

## 1. Imports

**Fichier : `frontend/app.py`**

- [ ] **Ligne 3** : Import `json` non utilisé
  - **Outil :** Ruff (F401)
  - **Gravité :** Faible
  - **Action :** Supprimer `import json`

---

## 2. Formatage

**Fichier : `frontend/app.py`**

- [ ] **Ligne 132** : f-string sans placeholder
  - **Code :** `st.error(f"### ACCIDENT GRAVE")`
  - **Outil :** Ruff (F541)
  - **Gravité :** Faible
  - **Action :** Remplacer par `st.error("### ACCIDENT GRAVE")`

- [ ] **Ligne 136** : f-string sans placeholder
  - **Code :** `st.success(f"### Accident non grave")`
  - **Outil :** Ruff (F541)
  - **Gravité :** Faible
  - **Action :** Remplacer par `st.success("### Accident non grave")`

---

## 3. Types

**Fichier : `frontend/app.py`**

- [ ] **Ligne 2** : Stubs manquants pour `requests`
  - **Outil :** Mypy (import-untyped)
  - **Gravité :** Moyenne
  - **Action :** `uv add --dev types-requests`

**Fichier : `backend/api.py`**

- [ ] **Ligne 2** : Stubs manquants pour `joblib`
  - **Outil :** Mypy (import-untyped)
  - **Gravité :** Moyenne
  - **Action :** Ajouter stubs ou ignorer

- [ ] **Ligne 3** : Stubs manquants pour `pandas`
  - **Outil :** Mypy (import-untyped)
  - **Gravité :** Moyenne
  - **Action :** `uv add --dev pandas-stubs`

- [ ] **Ligne 10, 14, 18** : Fonctions sans type de retour
  - **Fonctions :** `home()`, `health()`, `predict()`
  - **Outil :** Inspection manuelle
  - **Gravité :** Moyenne
  - **Action :** Ajouter `-> dict`

- [ ] **Ligne 28** : Type incompatible float → int
  - **Code :** `data['age'] = age`
  - **Outil :** Mypy
  - **Gravité :** Haute
  - **Action :** Typage cohérent du dictionnaire
  - **Statut :** CORRIGÉ : typage cohérent `dict[str, float]`

---

## 4. Documentation

**Fichier : `backend/api.py`**

- [ ] **Ligne 10** : Fonction `home()` sans docstring
- [ ] **Ligne 14** : Fonction `health()` sans docstring
- [ ] **Ligne 18** : Fonction `predict()` sans docstring
  - **Outil :** Inspection manuelle
  - **Gravité :** Moyenne
  - **Action :** Ajouter docstrings avec description, paramètres, retour
  - **Statut :** CORRIGÉ : docstrings ajoutées

---

## 5. Formatage (suite)

**Fichier : `backend/api.py`**

- [ ] **Ligne 5** : Espaces autour du `=` dans `title = "..."`
  - **Code :** `FastAPI(title = "...")`
  - **Outil :** Inspection manuelle
  - **Gravité :** Faible
  - **Action :** `FastAPI(title="...")`

- [ ] **Ligne 11, 15** : Pas d'espace après `return`
  - **Code :** `return{"message": ...}`
  - **Outil :** Inspection manuelle
  - **Gravité :** Faible
  - **Action :** `return {"message": ...}`

- [ ] **Ligne 11** : Espace avant `:` dans dictionnaire
  - **Code :** `"status" : "OK"`
  - **Outil :** Inspection manuelle
  - **Gravité :** Faible
  - **Action :** `"status": "OK"`

---

## 6. Sécurité

**Fichier : `backend/api.py`**

- [ ] **Ligne 18-19** : Pas de validation des entrées
  - **Problème :** Accepte n'importe quelle valeur (heure=9999, age=-50)
  - **Outil :** Inspection manuelle
  - **Gravité :** Haute
  - **Action :** Utiliser Pydantic pour valider les inputs
  - **Statut :** CORRIGÉ : `PredictionInput` ajouté

- [ ] **Ligne 7-8** : Pas de gestion d'erreur sur chargement modèle
  - **Problème :** Si fichier manquant → crash au démarrage
  - **Outil :** Inspection manuelle
  - **Gravité :** Haute
  - **Action :** try/except avec message d'erreur clair

---

## 7. Maintenabilité

**Fichier : `backend/api.py`**

- [ ] **Ligne 7-8** : Chemins en dur non configurables
  - **Code :** `"model_pred/model_logistic_regression.pkl"`
  - **Outil :** Inspection manuelle
  - **Gravité :** Moyenne
  - **Action :** Utiliser variables d'environnement ou config.py

---

## 8. Bugs

**Fichier : `backend/api.py`**

- [ ] **Ligne 56** : Variable `heure` non définie
  - **Code :** `or heure <= 6`
  - **Outil :** Inspection manuelle / Test
  - **Gravité :** CRITIQUE
  - **Action :** Remplacer par `input.heure`
  - **Statut :** CORRIGÉ - `input.heure`

- [ ] **Ligne 58** : Mélange int/float dans assignation
  - **Code :** `= 1 if ... else 0.0`
  - **Outil :** Inspection manuelle
  - **Gravité :** Faible
  - **Action :** Utiliser `1.0` pour cohérence
  - **Statut :** CORRIGÉ 

---

## 9. Compatibilité

**Fichier : `backend/api.py`**

- [ ] **Ligne 18-19** : Modèle entraîné avec scikit-learn 1.5.1, mais environnement utilise 1.8.0~~
  - **Outil :** Warning au démarrage
  - **Gravité :** Moyenne
  - **Action :** RÉSOLU - Modèle réentraîné avec scikit-learn 1.8.0
  - **Statut :** CORRIGÉ
  - **Statut :** CORRIGÉ - scikit-learn UPD à 1.8.0 et le modèle réentraîné

---

## 10. Breaking Changes

**Fichiers : `backend/api.py` + `frontend/app.py`**

- [ ] **Incompatibilité API/Frontend** : L'API attend maintenant un JSON body (Pydantic), mais le frontend envoie encore des query params
  - **Problème :** `frontend/app.py` utilise `requests.post(url, params=...)` au lieu de `requests.post(url, json=...)`
  - **Outil :** Test manuel (HTTP 422 Unprocessable Entity)
  - **Gravité :** CRITIQUE
  - **Action :** Modifier `frontend/app.py` pour envoyer les données en JSON dans le body
  - **Impact :** Le frontend ne fonctionne plus avec la nouvelle API

**Code actuel (frontend/app.py) :**
```python
params = {"heure": heure, "lum": lum, ...}
response = requests.post(url, params=params)  
```

**Code attendu :**
```python
data = {"heure": heure, "lum": lum, ...}
response = requests.post(url, json=data)  
```
---

## 11. Organisation du code

**Fichier : `backend/api.py`**

- [ ] **Toute la logique métier dans un seul fichier** : Prédiction, validation, chargement modèle dans le même fichier
  - **Outil :** Inspection manuelle
  - **Gravité :** Faible
  - **Action :** Séparer en modules (routes/, services/, models/)
  - **Meilleure pratique :** Structure MVC

---