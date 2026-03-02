# Prédiction de la Gravité des Accidents Routiers

Projet Machine Learning - Prédiction binaire (Grave / Non grave)

## Contexte

Ce projet utilise les données BAAC (Bulletins d'Analyse des Accidents Corporels) de 2022 à 2024 pour prédire la gravité d'un accident de la route en fonction de ses caractéristiques.

**Objectif :** Aider les services d'urgence à mobiliser les ressources adaptées en prédisant si un accident sera grave ou non.

---

## Structure du projet
```
accidents/
├── accidents.ipynb                      # Notebook principal (EDA, modélisation)
├── api.py                               # API FastAPI
├── app.py                               # Interface Streamlit
├── feature_names.json                   # Noms des features pour MLflow
├── confusion_matrix.png                 # Matrice de confusion exportée
├── roc_curve.png                        # Courbe ROC exportée
├── model_pred/
│   ├── model_logistic_regression.pkl    # Modèle entraîné (sélectionné)
│   ├── model_random_forest.pkl          # Modèle alternatif
│   └── model_columns.pkl               # Colonnes attendues
└── README.md                            # Documentation
```

---

## Résultats du modèle

**Modèle sélectionné :** Logistic Regression avec `class_weight = 'balanced'`

| Métrique | Valeur |
|----------|--------|
| **Recall (Grave)** | **66.8%** |
| Precision (Grave) | 32.4% |
| F1-Score | 0.44 |
| Accuracy | 68.9% |

**Interprétation :** Le modèle détecte 2 accidents graves sur 3, ce qui est acceptable dans un contexte de sécurité routière. La matrice de confusion révèle : 18 006 vrais négatifs, 7 957 faux positifs (fausses alertes), 1 895 faux négatifs (graves manqués) et 3 808 vrais positifs.

---

## Features principales

- **Temporelles** : heure, jour de la semaine, mois, weekend, nuit (22h–6h)
- **Conditions** : luminosité (`lum`), météo (`atm`), surface (`surf`), collision (`col`)
- **Route** : type de route (`catr`), localisation (`agg`, `int`), circulation, profil, plan, VMA
- **Véhicule** : catégorie (`catv`), obstacle, manœuvre, motorisation
- **Usager** : âge, sexe, catégorie (`catu`), trajet, équipement de sécurité, place
- **Features créées** : `jeune_conducteur` (< 25 ans), `conditions_dangereuses` (météo + luminosité + surface)

---

## Pipeline de données

Les données BAAC sont structurées en 4 fichiers par année (caract, lieux, vehicules, usagers) fusionnés selon la hiérarchie : accident → véhicule → usager. Les véhicules en fuite (~25% des données) sont exclus car leur variable cible (`grav`) est inconnue.

Le split entraînement/test est de **75/25**, stratifié sur la target.

---

## Expérimentations MLflow

Le projet utilise **MLflow** pour tracer et comparer les expériences :

- **Experiment 1 (`my-first-experiment`)** : Logistic Regression et Random Forest de base
- **Experiment 2 (`Tuning Random Forest`)** : tuning manuel (XGBoost_try1 à try4) avec ROC curve et feature importance loggées
- **GridSearchCV** : recherche sur `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf` (108 combinaisons, CV=5)
- **Optuna** : optimisation bayésienne sur Recall puis F1-score (10 trials)

---

## Facteurs de risque identifiés (EDA)

Les analyses exploratoires montrent que les accidents graves sont plus fréquents :

- La nuit (pics aux heures creuses, notamment 22h–6h)
- Le week-end (samedi et dimanche)
- Chez les jeunes conducteurs (< 25 ans) et les plus de 65 ans
- Par mauvaises conditions météo (pluie forte, neige, brouillard, vent)
- Sur routes départementales et hors agglomération
- Impliquant des deux-roues motorisés (motos > 125 cm³, quads, cyclomoteurs)

---

## Installation

### Prérequis

- Python 3.8+

### Installer les dépendances
```bash
pip install pandas numpy scikit-learn joblib missingno
pip install matplotlib seaborn
pip install mlflow optuna optuna-integration[mlflow]
pip install xgboost
pip install fastapi uvicorn
pip install streamlit requests
```

---

## Utilisation

### Lancer MLflow (suivi des expériences)
```bash
mlflow ui
```
Accéder à l'interface : http://localhost:5000

### Lancer l'API
```bash
uvicorn api:app --reload
```

Accéder à la documentation : http://127.0.0.1:8000/docs

### Lancer l'interface Streamlit

Dans un nouveau terminal :
```bash
streamlit run app.py
```

L'application s'ouvre sur : http://localhost:8501

---

## Données

**Source :** Base BAAC - data.gouv.fr  
**Années :** 2022, 2023, 2024  
**Volume :** 126 662 usagers (après exclusion des véhicules en fuite)

**Fichiers sources par année :** `caract-{year}.csv`, `lieux-{year}.csv`, `vehicules-{year}.csv`, `usagers-{year}.csv`

**Target :**
- **0 - Non grave** : Indemne + Blessé léger (82%)
- **1 - Grave** : Hospitalisé + Tué (18%)

---

## Technologies

- Python 3.11
- Pandas / NumPy / Missingno
- Scikit-learn
- MLflow
- Optuna
- XGBoost
- FastAPI
- Streamlit
- Uvicorn

---

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil |
| `/health` | GET | État de l'API |
| `/predict` | POST | Prédiction de gravité |

**Paramètres de `/predict`** (passés en query params) :

| Paramètre | Type | Plage | Défaut | Description |
|-----------|------|-------|--------|-------------|
| `heure` | int | 0–23 | 14 | Heure de l'accident |
| `lum` | int | 1–5 | 1 | Luminosité |
| `atm` | int | 1–6 | 1 | Conditions météo |
| `age` | float | 0–120 | 30 | Âge du conducteur |
| `catr` | int | 1–4 | 3 | Type de route |
| `agg` | int | 1–2 | 2 | Localisation (1=hors agglo, 2=agglo) |
| `sexe` | int | 1–2 | 1 | Sexe (1=masculin, 2=féminin) |
| `catv` | int | 1–33 | 7 | Type de véhicule |

Les features dérivées (`nuit`, `jeune_conducteur`, `conditions_dangereuses`) sont calculées automatiquement côté API.

---

## Déploiement avec Docker

### Prérequis

- Docker Desktop installé (version 20.10+)
- Docker Compose (version 2.0+)

### Installation rapide

#### Option 1 : Avec Docker Compose (recommandé)
```bash
# Cloner le repository
git clone https://github.com/inaongit/prediction-accidents.git
cd prediction-accidents

# Copier le fichier d'environnement
cp .env.example .env

# Lancer l'application
docker-compose up -d
```

**Accéder à l'application :**
- API : http://localhost:8000/docs
- Interface : http://localhost:8501

#### Option 2 : Avec les images DockerHub
```bash
# Télécharger et lancer l'API
docker run -d -p 8000:8000 --name accidents-api inaongit/accidents-api:v1.0

# Télécharger et lancer le Front
docker run -d -p 8501:8501 --name accidents-front \
  -e API_URL=http://accidents-api:8000 \
  --link accidents-api \
  inaongit/accidents-front:v1.0
```

### Commandes utiles
```bash
# Démarrer les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose up --build

# Nettoyer tout
docker-compose down -v
```

### Images DockerHub

Les images sont disponibles publiquement :
- API : https://hub.docker.com/r/inaongit/accidents-api
- Front : https://hub.docker.com/r/inaongit/accidents-front
```bash
docker pull inaongit/accidents-api:v1.0
docker pull inaongit/accidents-front:v1.0
```

### Variables d'environnement

Voir le fichier `.env.example` pour la liste complète des variables.

| Variable | Description | Défaut |
|----------|-------------|--------|
| API_URL | URL de l'API | http://api:8000 |
| ENVIRONMENT | Environnement | production |
