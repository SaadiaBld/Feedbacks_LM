from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum
import sys
import os

# 📌 Ajout des chemins vers tes modules perso
sys.path.append("/opt/airflow/project/scripts_data")
sys.path.append("/opt/airflow/project/api")

from dotenv import load_dotenv
load_dotenv(dotenv_path="/opt/airflow/.env")

# 📌 Import des fonctions Python
from scripts_data.scraper import scrape_reviews
from scripts_data.cleaner import clean_data
from api.analyze_and_insert import process_and_insert_all
from scripts_data.main import main as run_full_scraper_pipeline

# Wrapper pour le scraper
def wrapper_run_scraper(**context):
    scrape_date = context["ds"]  # date de l'exécution du DAG (au format YYYY-MM-DD)
    print(f"📆 Wrapper Scraper : scrape_date = {scrape_date}")
    # Tu peux passer la date à scrape_reviews si besoin, ou la logguer pour audit
    scrape_reviews(mode="csv")  # Ici, le scraper utilise utc.today() - 15j (exemple)

# Wrapper pour analyse & insertion
def wrapper_process_and_insert(**context):
    scrape_date = context["ds"]
    print(f"📆 Wrapper Analyse/Insert : scrape_date = {scrape_date}")
    process_and_insert_all(scrape_date=scrape_date)


# Paramètres par défaut
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG
with DAG(
    dag_id='trustpilot_pipeline',
    default_args=default_args,
    description='Pipeline : Scraper → Nettoyage → Claude → BQ',
    schedule_interval='0 6 * * 1',  # chaque lundi à 6h (heure de Paris)
    start_date=datetime(2025, 6, 1, tzinfo=pendulum.timezone("Europe/Paris")),
    catchup=False,
    tags=['trustpilot', 'nlp', 'bq'],
) as dag:

    # Scraping
    scrape_task = PythonOperator(
        task_id='scrape_trustpilot_reviews',
        python_callable=run_full_scraper_pipeline
    )

    # Nettoyage CSV
    clean_task = PythonOperator(
        task_id='clean_reviews',
        python_callable=clean_data,
    )

    # Analyse + Insertion
    analyze_insert_task = PythonOperator(
        task_id='analyze_and_insert',
        python_callable=wrapper_process_and_insert,
        provide_context=True,
    )

    # Orchestration
    scrape_task >> clean_task >> analyze_insert_task
