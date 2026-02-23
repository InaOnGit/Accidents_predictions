import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

with patch('joblib.load') as mock_load:
    mock_model = Mock() #on crée des mocks des vrais modèles qui sont commentés dans dockerfile
    mock_model.predict.return_value = [0]  #préd "Non grave"
    mock_model.predict_proba.return_value = [[0.7, 0.3]]  #probas
    
    mock_columns = ['heure', 'lum', 'atm', 'age', 'catr', 'agg', 'sexe', 'catv',
                    'nuit', 'jeune_conducteur', 'conditions_dangereuses']
    
    mock_load.side_effect = [mock_model, mock_columns]
    
    from api import app

client = TestClient(app)

def test_home():
    """Test du endpoint racine."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_health():
    """Test du endpoint health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["model"] == "Logistic Regression"


def test_predict_valid_input():
    """Test de prédiction avec données valides."""
    data = {
        "heure": 14,
        "lum": 1,
        "atm": 1,
        "age": 30,
        "catr": 3,
        "agg": 2,
        "sexe": 1,
        "catv": 7
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 200
    result = response.json()
    assert "gravite" in result
    assert "probabilite_grave" in result
    assert "probabilite_non_grave" in result
    assert result["gravite"] in ["Grave", "Non grave"]


def test_predict_invalid_age():
    """Test avec âge invalide."""
    data = {
        "heure": 14,
        "lum": 1,
        "atm": 1,
        "age": 150,  #invalide
        "catr": 3,
        "agg": 2,
        "sexe": 1,
        "catv": 7
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 422  #valid error


def test_predict_invalid_heure():
    """Test avec heure invalide."""
    data = {
        "heure": 25,  #invalide
        "lum": 1,
        "atm": 1,
        "age": 30,
        "catr": 3,
        "agg": 2,
        "sexe": 1,
        "catv": 7
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 422  #valid error