import os
import uuid
import pytest
from datetime import date
from google.cloud import bigquery


# Récupération des variables d'environnement injectées via GitHub Actions
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")

# Construction des identifiants complets des tables
REVIEWS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.reviews"
TOPIC_ANALYSIS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.topic_analysis"

@pytest.mark.skipif(not PROJECT_ID, reason="Les credentials GCP ne sont pas configurés")
def test_insert_review_table():
    """
    Vérifie l'insertion dans la table 'reviews' via une insertion réelle.
    """
    client = bigquery.Client(project=PROJECT_ID)

    # Génération d'un review_id unique pour l'intégration
    review_id = f"test-ci-{uuid.uuid4()}"
    review_row = {
        "review_id": review_id,
        "rating": 2,
        "content": "TEST: Produit arrivé cassé",
        "author": "test_user",
        "publication_date": date.today().isoformat(),
        "scrape_date": date.today().isoformat()
    }

    # Insertion de la ligne dans la table 'reviews'
    errors = client.insert_rows_json(REVIEWS_TABLE, [review_row])
    assert errors == [], f"Erreur d'insertion dans 'reviews' : {errors}"

    # Vérification via une requête SELECT
    query = f"""
        SELECT review_id, rating, content, author 
        FROM `{REVIEWS_TABLE}` 
        WHERE review_id = '{review_id}'
    """
    rows = list(client.query(query).result())
    assert len(rows) == 1, "La ligne review n'a pas été retrouvée après insertion"
    row = rows[0]
    assert row.review_id == review_id
    assert row.rating == 2
    assert row.content == "TEST: Produit arrivé cassé"
    assert row.author == "test_user"

    #Cleanup après test
    cleanup = f"DELETE FROM `{REVIEWS_TABLE}` WHERE review_id = '{review_id}'"
    client.query(cleanup).result()

@pytest.mark.skipif(not PROJECT_ID, reason="Les credentials GCP ne sont pas configurés")
def test_insert_topic_analysis_table():
    """
    vérifie l'insertion dans la table 'topic_analysis' en utilisant la fonction 
    insert_topic_analysis de notre module, puis vérifie que deux lignes ont été insérées.
    """
    # Importation de la fonction à tester
    from api.analyze_and_insert import insert_topic_analysis

    client = bigquery.Client(project=PROJECT_ID)

    # Génération d'un review_id unique pour ce test d'intégration
    review_id = f"test-ci-{uuid.uuid4()}"
    theme_scores = [
        {"theme": "Livraison et retrait", "note": 3},
        {"theme": "Retour et remboursement", "note": 4}
    ]
    
    label_to_id= { 
        "Livraison et retrait": 2,
        "Retour et remboursement": 3
    }

    # Appel de la fonction d'insertion réelle
    result = insert_topic_analysis(review_id, theme_scores, label_to_id)
    assert result is not None, "Aucun résultat retourné par insert_topic_analysis"
    assert result["insert_errors"] == False, "Erreur lors de l'insertion dans 'topic_analysis'"

    # Vérification via une requête SELECT sur la table topic_analysis
    query = f"""
        SELECT review_id, topic_id, score_sentiment, label_sentiment, score_0_1
        FROM `{TOPIC_ANALYSIS_TABLE}`
        WHERE review_id = '{review_id}'
    """
    rows = list(client.query(query).result())
    # Nous nous attendons à deux lignes insérées pour deux thèmes traités
    assert len(rows) == 2, f"Nombre de lignes insérées dans 'topic_analysis' attendu : 2, obtenu : {len(rows)}"
    for row in rows:
        assert row.review_id == review_id
        # Vous pouvez ajouter d'autres assertions sur les valeurs de score_sentiment, label_sentiment, etc.
        assert row.score_sentiment in [3, 4], f"Score sentiment inattendu : {row.score_sentiment}"
        assert row.label_sentiment in ["Neutre", "Positif"], f"Label sentiment inattendu : {row.label_sentiment}"
        assert isinstance(row.score_0_1, float), f"score_0_1 doit être un float, obtenu : {row.score_0_1}"

    # Cleanup après test
    cleanup = f"DELETE FROM `{TOPIC_ANALYSIS_TABLE}` WHERE review_id = '{review_id}'"
    client.query(cleanup).result()