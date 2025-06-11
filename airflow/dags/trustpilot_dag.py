from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.append("/opt/airflow/project")

# 🔧 Ajoute le chemin du projet racine pour pouvoir importer tes modules Python
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

from api.analyze_and_insert import run_analysis

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["ton_email@gmail.com"],  # optionnel
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="trustpilot_verbatim_analysis",
    description="Analyse et insertion automatique des verbatims dans BigQuery",
    default_args=default_args,
    start_date=datetime(2025, 6, 10),
    schedule_interval="@daily",  # ou "0 7 * * *" pour tous les jours à 7h
    catchup=False,
    tags=["trustpilot", "claude", "bigquery"]
) as dag:

    def analyze_today():
        today_str = datetime.utcnow().strftime("%Y-%m-%d")        
        run_analysis(scrape_date=today_str)

    task_analyze = PythonOperator(
        task_id="analyze_and_store_verbatims",
        python_callable=analyze_today,
    )

    task_analyze