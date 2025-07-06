from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pendulum
import sys
import os
import logging

from dotenv import load_dotenv
load_dotenv("/opt/airflow/project/.env")

# 📌 Ajout des chemins
sys.path.append("/opt/airflow/project/scripts_data")
sys.path.append("/opt/airflow/project/api")

# 📌 Import safe
from scripts_data.scraper import scrape_reviews
from scripts_data.cleaner import clean_data
from scripts_data.main import main as run_full_scraper_pipeline

try:
    from api.analyze_and_insert import process_and_insert_all
    PROCESS_AVAILABLE = True
except FileNotFoundError as e:
    logging.error(f"❌ Fichier manquant empêchant l'import : {e}")
    process_and_insert_all = None
    PROCESS_AVAILABLE = False

print("📁 Fichier .env chargé")
print("👉 Mode scraping :", os.getenv("SCRAPER_MODE"))
print("👉 Fichier d’entrée :", os.getenv("INPUT_CSV"))


# Wrappers
def wrapper_run_scraper(**context):
    scrape_date = context["ds"]
    print(f"📆 Wrapper Scraper : scrape_date = {scrape_date}")
    scrape_reviews()


def wrapper_process_and_insert(**context):
    scrape_date = context["ds"]
    print(f"📆 Wrapper Analyse/Insert : scrape_date = {scrape_date}")
    print("📂 Fichier de credentials GCP : ", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    if process_and_insert_all:
        process_and_insert_all(scrape_date=scrape_date)
    else:
        raise RuntimeError("Fonction d’analyse non disponible. Vérifiez le fichier de credentials.")


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
    schedule_interval= None, #'0 6 * * 1',
    start_date=datetime(2025, 6, 1, tzinfo=pendulum.timezone("Europe/Paris")),
    catchup=False,
    tags=['trustpilot', 'nlp', 'bq'],
) as dag:

    # Scraping
    scrape_task = PythonOperator(
        task_id='scrape_trustpilot_reviews',
        python_callable=wrapper_run_scraper,
        provide_context=True,
    )

    # Nettoyage
    clean_task = PythonOperator(
        task_id='clean_reviews',
        python_callable=clean_data,
    )

    # Analyse / Insertion ou Dummy si process indisponible
    if PROCESS_AVAILABLE:
        analyze_insert_task = PythonOperator(
            task_id='analyze_and_insert',
            python_callable=wrapper_process_and_insert,
            provide_context=True,
        )
    else:
        analyze_insert_task = DummyOperator(task_id='skip_analyze_insert_due_to_missing_cred')

    # Orchestration
    scrape_task >> clean_task >> analyze_insert_task
