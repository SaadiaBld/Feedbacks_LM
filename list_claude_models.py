#script qui verifier la disponibilité des modèles Claude d'Anthropic
# pour l'appeler dans le script de classification des verbatims

import anthropic
import os
from dotenv import load_dotenv
from pathlib import Path

# Chargement de la clé API depuis le .env
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("❌ Clé API manquante dans .env (ANTHROPIC_API_KEY)")

client = anthropic.Anthropic(api_key=api_key)

# Liste des modèles possibles connus (mise à jour manuelle si besoin)
KNOWN_MODELS = [
    "claude-3-haiku-20240307",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229"
]

print("🔍 Test de disponibilité des modèles Claude avec votre clé :\n")

for model in KNOWN_MODELS:
    try:
        # Envoie un message minimal pour tester le modèle
        response = client.messages.create(
            model=model,
            max_tokens=5,
            messages=[{"role": "user", "content": "Test"}],
        )
        print(f"✅ Modèle disponible : {model}")
    except anthropic.APIStatusError as e:
        print(f"❌ Modèle indisponible : {model} — {e.status_code} / {e.message}")
    except Exception as e:
        print(f"❌ Erreur inattendue avec {model} : {e}")
