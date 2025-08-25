import os
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
from scripts_data.scraper import scrape_reviews
from scripts_data.cleaner import clean_csv
from api.classify import run as classify_and_store

# Les variables d'environnement (ex: PROJECT_ID) sont gérées par GCP, .env est inutile ici

# === Variables globales ===
PROJECT_ID = os.getenv("PROJECT_ID", "trustpilot-satisfaction")
TARGET_TABLE = f"{PROJECT_ID}.reviews_dataset.reviews"
TEMP_TABLE = f"{PROJECT_ID}.reviews_dataset.temp_reviews"
SCRAPER_MODE = os.getenv("SCRAPER_MODE", "csv")
INPUT_FILE = "/tmp/avis_boutique.csv"
OUTPUT_FILE = "/tmp/avis_boutique_clean.csv"


def upload_to_bigquery(csv_path: str, target_table_id: str):
    df = pd.read_csv(csv_path)
    expected_columns = ['review_id', 'rating', 'content', 'author', 'publication_date', 'scrape_date']
    
    if list(df.columns) != expected_columns:
        raise ValueError(f"Le CSV ne contient pas les colonnes attendues : {expected_columns}")

    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce').dt.date
    df['scrape_date'] = pd.to_datetime(df['scrape_date'], errors='coerce').dt.date

    client = bigquery.Client()

    # Étape 1 : chargement dans une table temporaire
    load_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(df, TEMP_TABLE, job_config=load_config).result()
    print(f"Données chargées dans {TEMP_TABLE}.")

    # Étape 2 : MERGE dans la table finale (sans doublon sur review_id)
    merge_query = f"""
        MERGE `{target_table_id}` T
        USING `{TEMP_TABLE}` S
        ON T.review_id = S.review_id
        WHEN NOT MATCHED THEN
            INSERT (review_id, rating, content, author, publication_date, scrape_date)
            VALUES (S.review_id, S.rating, S.content, S.author, S.publication_date, S.scrape_date)
    """
    client.query(merge_query).result()
    print(f"Données fusionnées dans {target_table_id}.")


def run_pipeline():
    """Exécute le pipeline complet de traitement des données."""
    print(f"\n Début du pipeline à {datetime.utcnow().isoformat()}")
    print(f"Mode scraping sélectionné : {SCRAPER_MODE}")

    if SCRAPER_MODE == "csv":
        print("Mode CSV pour test local : on lit un fichier de test")
    else:
        print("Scraping Trustpilot en ligne...")
        scrape_reviews(mode="csv")  # force la sortie en CSV 

    print("Nettoyage des données CSV...")
    clean_stats = clean_csv(INPUT_FILE, OUTPUT_FILE)
    print(f"Statistiques de nettoyage : {clean_stats}")

    print("📤 Upload des données dans BigQuery...")
    try:
        upload_to_bigquery(OUTPUT_FILE, TARGET_TABLE)
    except Exception as e:
        # Message d'erreur spécifique pour BigQuery !
        print(f"❌ Erreur critique lors du stockage dans BigQuery : {e}")
        # On propage l'erreur pour que la fonction principale échoue quand même
        raise

    today = datetime.utcnow().date().isoformat()
    print("🤖 Lancement de l'analyse Claude...")
    try:
        classify_and_store(scrape_date=today)
    except Exception as e:
        # Message d'erreur spécifique pour l'analyse Claude !
        print(f"❌ Erreur critique lors de l'analyse Claude et du stockage dans topic_analysis : {e}")
        raise

    print("✅ Pipeline complet exécuté avec succès.")


def main(request=None):
    """Point d'entrée de la Cloud Function HTTP."""
    try:
        run_pipeline()
        return ("OK: Pipeline exécuté avec succès.", 200)
    except Exception as e:
        print(f"Erreur critique dans le pipeline : {e}")
        return (f"Erreur : {e}", 500)
