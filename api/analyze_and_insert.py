from bq_connect import get_verbatims_by_date
from claude_interface import classify_with_claude
from google.cloud import bigquery
import uuid

def load_topic_ids():
    client = bigquery.Client()
    query = """
        SELECT topic_label, topic_id
        FROM `trustpilot-satisfaction.reviews_dataset.topics`
    """
    results = client.query(query).result()
    return {row.topic_label: row.topic_id for row in results}


def insert_topic_analysis(review_id: str, theme_scores: list[dict], label_to_id: dict):
    client = bigquery.Client()
    rows_to_insert = []

    if len(theme_scores) == 0:
        print("⚠️ Aucun thème détecté")
        return

    for item in theme_scores:
        theme = item["theme"]
        note = item["note"]
        topic_id = label_to_id.get(theme)

        if not topic_id:
            print(f"⚠️ Thème inconnu dans la table topics : {theme}")
            continue

        # Score de satisfaction normalisé (1 = très insatisfait, 0 = très satisfait)
        score_0_1 = round((5 - note) / 4, 2)

        # Label de satisfaction
        if score_0_1 >= 0.85:
            label = "Très négatif"
        elif score_0_1 >= 0.65 and score_0_1 < 0.85:
            label = "Négatif"
        elif score_0_1 >= 0.4 and score_0_1 < 0.65:
            label = "Neutre"
        elif score_0_1 >= 0.25 and score_0_1 < 0.4:
            label = "Positif"
        else:
            label = "Très positif"

        rows_to_insert.append({
            "id": str(uuid.uuid4()),
            "review_id": review_id,
            "topic_id": topic_id,  # Le thème détecté devient la valeur de topic_id
            "score_sentiment": note,
            "label_sentiment": label,
            "score_0_1": score_0_1
        })
    if not rows_to_insert:
        print("⚠️ Aucun thème à insérer")
        return
    
    errors = client.insert_rows_json("trustpilot-satisfaction.reviews_dataset.topic_analysis", rows_to_insert)

    if errors:
        print(f"❌ Erreurs d'insertion : {errors}")
    else:
        print(f"✅ {len(rows_to_insert)} lignes insérées pour review {review_id}")
        print("📊 Thèmes détectés :")
        for r in rows_to_insert:
            print(f" - {r['topic_id']} (note : {r['score_sentiment']})")

def run_analysis(scrape_date: str):
    verbatims = get_verbatims_by_date(scrape_date)
    label_to_id = load_topic_ids()

    print(f"📅 {len(verbatims)} verbatims trouvés pour la date : {scrape_date}")

    for i, v in enumerate(verbatims):
        print(f"\n🟦 Verbatim {i+1} :\n{v['content']}")
        
        theme_scores = classify_with_claude(v["content"])

        # Afficher la réponse brute de Claude pour debug
        print("\n📥 Réponse brute de Claude :")
        print(theme_scores)

        if theme_scores:
            insert_topic_analysis(
                review_id=v["review_id"],
                theme_scores=theme_scores,
                label_to_id=label_to_id
            )
        else:
            print("❌ Analyse non exploitable (voir claude_errors.log)")

if __name__ == "__main__":
    run_analysis("2025-06-09")
