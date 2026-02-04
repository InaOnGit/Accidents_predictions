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
├── model_logistic_regression.pkl        # Modèle entraîné
├── model_random_forest.pkl              # Modèle alternatif
├── model_columns.pkl                    # Colonnes attendues
├── .streamlit/
│   └── config.toml                      # Configuration thème
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

**Interprétation :** Le modèle détecte 2 accidents graves sur 3, ce qui est acceptable dans un contexte de sécurité routière.

---

## Features principales

- **Temporelles** : heure, jour de la semaine, weekend, nuit
- **Conditions** : luminosité, météo, surface
- **Route** : type de route, localisation
- **Usager** : âge, sexe, type de véhicule
- **Features créées** : jeune_conducteur, conditions_dangereuses

---

## Installation

### Prérequis

- Python 3.8+

### Installer les dépendances
```bash
pip install pandas numpy scikit-learn joblib
pip install fastapi uvicorn
pip install streamlit requests
```

---

## Utilisation

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
**Volume :** 126,662 usagers

**Target :**
- **0 - Non grave** : Indemne + Blessé léger (82%)
- **1 - Grave** : Hospitalisé + Tué (18%)

---

## Technologies

- Python 3.11
- Pandas / NumPy
- Scikit-learn
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

---

## Facteurs de risque identifiés

Les accidents graves sont plus fréquents :

- La nuit (22h-6h)
- Jeunes conducteurs (<25 ans)
- Mauvaises conditions météo
- Routes départementales
- Hors agglo

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