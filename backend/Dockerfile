FROM python:3.11-slim

LABEL maintainer="inaongit"
LABEL version="1.0"
LABEL description="API de prédiction de gravité d'accidents routiers"
LABEL project="prediction-accidents"

WORKDIR /backend
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]