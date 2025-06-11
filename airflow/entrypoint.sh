#!/bin/bash

pip install -r /requirements.txt

airflow db init

# Crée l'utilisateur admin si non existant
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin || true

exec airflow webserver