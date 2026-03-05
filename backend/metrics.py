from prometheus_client import Counter, Gauge, Histogram

predictions_total = Counter(
    'prediction_total', 
    'nombre total des prédictions effectuées', 
    ['gravite']
)

http_errors_total = Counter(
    'http_errors_total',
    'nombre total d\'erreurs HTTP',
    ['error_type', 'endpoint'] 
)

probability_histogram = Histogram(
    'prediction_probability',
    'distribution des probabilités de prédiction',
    ['gravite'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

app_uptime_seconds = Gauge(
    'app_uptime_seconds',
    'temps depuis le démarrage de l\'application en secondes'
)

model_inference_duration_seconds = Histogram(
    'model_inference_duration_seconds',
    'durée de l\'inférence du modèle ML en secondes'
)