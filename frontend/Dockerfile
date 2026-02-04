FROM python:3.11-slim

LABEL maintainer="inaongit"
LABEL version="1.0"
LABEL description="Interface Streamlit pour prédiction d'accidents"
LABEL project="prediction-accidents"

WORKDIR /frontend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . . 
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
