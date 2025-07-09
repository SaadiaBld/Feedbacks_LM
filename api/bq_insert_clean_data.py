
import pandas as pd
from google.cloud import bigquery
import os

def insert_clean_reviews_to_bq():
    path = "/opt/airflow/project/data/avis_boutique_clean.csv"
    table_id = "trustpilot-satisfaction.reviews_dataset.reviews"

    if not os.path.exists(path):
        print(f"❌ Le fichier {path} n'existe pas.")
        return

    df = pd.read_csv(path)

    if df.empty:
        print("⚠️ Le fichier nettoyé est vide. Rien à insérer dans BigQuery.")
        return

    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # ou WRITE_TRUNCATE
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )

    with open(path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)

    try:
        job.result()  # Attendre la fin
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion dans BigQuery : {e}")
        return
    
    print(f"✅ {df.shape[0]} lignes insérées dans {table_id}")
