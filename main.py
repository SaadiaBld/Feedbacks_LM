from google.cloud import bigquery
import pandas as pd
from scraper import scrape_reviews
from cleaner import clean_csv
from datetime import datetime

def upload_to_bigquery(csv_path, target_table_id):
    df = pd.read_csv(csv_path)

    # Convertir publication_date en datetime.date
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce').dt.date
    df['scrape_date'] = pd.to_datetime(df['scrape_date'], errors='coerce').dt.date

    client = bigquery.Client()

    #table temporaire dans bq
    temp_table_id = "trustpilot-satisfaction.reviews_dataset.temp_reviews"

    #upload dans la table temporaire
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, temp_table_id, job_config=job_config)
    job.result()  # Attendre la fin du job
    print(f"✅ Données chargées dans la table temporaire {temp_table_id}.")

    #verifier les colonnes du df
    expected_columns = ['review_id', 'rating', 'content', 'author', 'publication_date', 'scrape_date']
    if not expected_columns == list(df.columns):
        raise ValueError(f"Le DataFrame ne contient pas les colonnes attendues : {expected_columns}")
    
    #merger les données de la table temporaire dans la table finale
    merge_query = f"""
    MERGE `{target_table_id}` T
    USING `{temp_table_id}` S
    ON T.review_id = S.review_id
    WHEN NOT MATCHED THEN
        INSERT (review_id, rating, content, author, publication_date, scrape_date)
        VALUES (S.review_id, S.rating, S.content, S.author, S.publication_date, S.scrape_date)
    """

    query_job = client.query(merge_query)
    query_job.result()  # Attendre la fin du job
    print(f"✅ Données fusionnées dans la table {target_table_id}.")



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