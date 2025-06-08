from google.cloud import bigquery
import pandas as pd
from scraper import scrape_reviews
from cleaner import clean_csv
from datetime import datetime

def upload_to_bigquery(csv_path, table_id):
    df = pd.read_csv(csv_path)

    # Convertir publication_date en datetime.date
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce').dt.date
    df['scrape_date'] = pd.to_datetime(df['scrape_date'], errors='coerce').dt.date

    client = bigquery.Client()
    job = client.load_table_from_dataframe(df, table_id)
    job.result()
    print(f"{len(df)} lignes insérées dans {table_id}.")
    print(f"✅ Données chargées dans BigQuery : {table_id}")

def main():
    print("▶ Début du scraping à", datetime.now().isoformat())
    # Scraping et sauvegarde directe dans CSV
    scrape_reviews(mode='csv')  # stocke dans data/avis_boutique.csv

    print("▶ Début du nettoyage à", datetime.now().isoformat())
    input_file = 'data/avis_boutique.csv'
    output_file = 'data/avis_nettoyes.csv'
    clean_csv(input_file, output_file)

    print("▶ Upload dans BigQuery...")
    upload_to_bigquery(output_file, "trustpilot-satisfaction.reviews_dataset.reviews")

    print("✅ Pipeline terminé avec succès.")

if __name__ == "__main__":
    main()