import os
from google.cloud import bigquery
from dotenv import load_dotenv

from api.claude_interface import classify_with_claude
from api.analyze_and_insert import insert_topic_analysis, load_topic_ids

# === Chargement des variables d'environnement ===
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("⚠️ .env introuvable, on continue avec les variables d'environnement GCP.")

# === Authentification BigQuery via fichier de credentials ===
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "credentials.json")

# === Paramètres ===
REVIEW_ID = "9133b8b25432784c238d15b1e1e11d91"
PROJECT_ID = os.getenv("PROJECT_ID", "trustpilot-satisfaction")
REVIEWS_TABLE = f"{PROJECT_ID}.reviews_dataset.reviews"

# === Étape 1 : Récupérer le contenu du verbatim ===
client = bigquery.Client()
query = f"""
    SELECT content
    FROM `{REVIEWS_TABLE}`
    WHERE review_id = '{REVIEW_ID}'
"""
rows = list(client.query(query).result())
if not rows:
    print("❌ Aucune review trouvée avec cet ID.")
    exit()

content = rows[0].content
print(f"📄 Verbatim à analyser :\n{content}\n")

# === Étape 2 : Appel à Claude ===
results = classify_with_claude(content)
if not results:
    print("⚠️ Claude n’a rien renvoyé.")
    exit()

# === Étape 3 : Insertion dans topic_analysis ===
label_to_id = load_topic_ids()
insert_result = insert_topic_analysis(REVIEW_ID, results, label_to_id)
print("✅ Résultat de l’insertion :", insert_result)
