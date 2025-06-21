# monitoring/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Copier seulement les fichiers nécessaires
COPY . ./

# Installer les dépendances (prometheus_client, etc.)
RUN pip install --no-cache-dir prometheus_client

# Démarrer le serveur d'export de métriques
CMD ["python", "exporter.py"]
