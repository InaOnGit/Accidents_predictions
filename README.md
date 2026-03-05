# Prédiction de la Gravité des Accidents Routiers

Projet Machine Learning - Prédiction binaire (Grave / Non grave) avec monitoring Prometheus/Grafana

## Contexte

Ce projet utilise les données BAAC (Bulletins d'Analyse des Accidents Corporels) de 2022 à 2024 pour prédire la gravité d'un accident de la route en fonction de ses caractéristiques.

**Objectif :** Aider les services d'urgence à mobiliser les ressources adaptées en prédisant si un accident sera grave ou non.

---

## Structure du projet
```
accidents/
├── backend/
│   ├── api.py                  # API FastAPI instrumentée
│   ├── metrics.py              # Métriques Prometheus custom
│   ├── Dockerfile              # Build de l'API
│   └── model_pred/             # Modèles ML entraînés
├── frontend/
│   ├── app.py                  # Interface Streamlit
│   └── Dockerfile              # Build du frontend
├── notebooks/
│   └── accidents.ipynb         # Notebook EDA + modélisation + MLflow
├── dashboards/
│   ├── http_overview.json      # Dashboard Grafana HTTP
│   └── predictions_ml.json     # Dashboard Grafana ML
├── docker-compose.yml          # Stack complète (API, Prometheus, Grafana)
├── prometheus.yml              # Configuration Prometheus
└── README.md                   # Documentation
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

## Monitoring & Observabilité

Le projet intègre une stack complète de monitoring avec **Prometheus** et **Grafana**.

### Architecture de monitoring

```
API FastAPI (/metrics) → Prometheus → Grafana (Dashboards)
     ↓                        ↓
 Métriques custom      node-exporter (métriques système)
                       cAdvisor (métriques containers)
```

### Métriques collectées

#### Métriques applicatives (custom)
- `prediction_total` : Nombre total de prédictions par gravité
- `prediction_probability` : Distribution des probabilités de prédiction
- `model_inference_duration_seconds` : Latence d'inférence du modèle ML
- `http_errors_total` : Erreurs HTTP par type et endpoint
- `app_uptime_seconds` : Temps depuis le démarrage de l'application

#### Métriques HTTP (automatiques via FastAPI Instrumentator)
- `http_requests_total` : Nombre de requêtes par méthode, endpoint et status
- `http_request_duration_seconds` : Latence des requêtes HTTP
- `http_requests_inprogress` : Nombre de requêtes en cours

#### Métriques infrastructure
- **node-exporter** : CPU, RAM, disque, réseau
- **cAdvisor** : Métriques des containers Docker

### Dashboards Grafana

**Dashboard 1 : HTTP Overview**
- Requêtes par seconde
- Latence P95
- Taux d'erreur
- Requêtes en cours
- CPU Usage %
- Memory Usage %

**Dashboard 2 : Prédictions ML**
- Total des prédictions
- Prédictions par gravité (Grave/Non grave)
- Probabilité moyenne
- Latence d'inférence du modèle
- Erreurs par type
- CPU par container

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

## Technologies

- **Backend** : Python 3.11, FastAPI, Uvicorn
- **ML** : Scikit-learn, Pandas, NumPy
- **MLOps** : MLflow, Optuna, XGBoost
- **Frontend** : Streamlit
- **Monitoring** : Prometheus, Grafana, prometheus-client, prometheus-fastapi-instrumentator
- **Infrastructure** : Docker, Docker Compose, node-exporter, cAdvisor

---

## Installation et déploiement

### Prérequis

- Docker Desktop (version 20.10+)
- Docker Compose (version 2.0+)

### Déploiement complet avec Docker Compose

```bash
# Cloner le repository
git clone https://github.com/inaongit/Accidents_predictions.git
cd Accidents_predictions

# Lancer la stack complète
docker compose up -d
```

### Accéder aux services

Une fois la stack lancée, vous pouvez accéder à :

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | API FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentation Swagger |
| **Métriques** | http://localhost:8000/metrics | Endpoint Prometheus |
| **Frontend** | http://localhost:8501 | Interface Streamlit |
| **Prometheus** | http://localhost:9090 | Interface Prometheus |
| **Grafana** | http://localhost:3000 | Dashboards (admin/admin) |
| **node-exporter** | http://localhost:9100/metrics | Métriques système |
| **cAdvisor** | http://localhost:8080 | Métriques containers |

### Commandes utiles

```bash
# Démarrer tous les services
docker compose up -d

# Voir les logs
docker compose logs -f

# Voir les logs d'un service spécifique
docker compose logs -f api

# Arrêter les services
docker compose down

# Reconstruire et redémarrer
docker compose up -d --build

# Nettoyer tout (containers, volumes, networks)
docker compose down -v
```

### Importer les dashboards Grafana

1. Se connecter à Grafana : http://localhost:3000 (admin/admin)
2. Menu → **Dashboards** → **Import**
3. Cliquer **Upload JSON file**
4. Sélectionner `dashboards/http_overview.json` ou `dashboards/predictions_ml.json`
5. Sélectionner **Prometheus** comme data source
6. Cliquer **Import**

---

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil |
| `/health` | GET | État de l'API + uptime |
| `/predict` | POST | Prédiction de gravité |
| `/metrics` | GET | Métriques Prometheus |

### Paramètres de `/predict`

**Body JSON :**

```json
{
  "heure": 14,
  "lum": 1,
  "atm": 1,
  "age": 30,
  "catr": 3,
  "agg": 2,
  "sexe": 1,
  "catv": 7
}
```

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

Les features dérivées (`nuit`, `jeune_conducteur`, `conditions_dangereuses`) sont calculées automatiquement.

---

## Données

**Source :** Base BAAC - data.gouv.fr  
**Années :** 2022, 2023, 2024  
**Volume :** 126 662 usagers (après exclusion des véhicules en fuite)

**Target :**
- **0 - Non grave** : Indemne + Blessé léger (82%)
- **1 - Grave** : Hospitalisé + Tué (18%)

---

## Facteurs de risque identifiés

Les analyses exploratoires montrent que les accidents graves sont plus fréquents :

- La nuit (22h–6h)
- Le week-end
- Chez les jeunes conducteurs (< 25 ans) et les plus de 65 ans
- Par mauvaises conditions météo
- Sur routes départementales et hors agglomération
- Impliquant des deux-roues motorisés
