import anthropic
import os
import json
import logging
from dotenv import load_dotenv
from pathlib import Path
from .prompt_utils import build_prompt, THEMES
from typing import Optional, List, Dict, Union

# Assurez-vous que ANTHROPIC_API_KEY est définie dans l'environnement GCP.

# === Récupération de la clé API Anthropic ===
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise EnvironmentError("❌ Clé API ANTHROPIC_API_KEY non définie dans l’environnement.")

client = anthropic.Anthropic(api_key=api_key)
THEME_LABELS = {t["nom"] for t in THEMES}

# === Setup du logger pour Cloud Functions (stdout uniquement) ===
logger = logging.getLogger("claude_logger")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)


def classify_with_claude(verbatim: str) -> Optional[List[Dict[str, Union[str, float]]]]:
    prompt = build_prompt(verbatim)
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            temperature=0,
            system="Tu es un assistant d’analyse de satisfaction client.",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text.strip()
        print("▶ Réponse Claude brute :\n", content)

        validated = validate_claude_response(content)
        if not validated:
            logger.warning(f"Réponse non valide : {content}")
        return validated

    except Exception as e:
        logger.error(f"❌ Erreur API Claude : {e}")
        raise


def validate_claude_response(response_text: str) -> Optional[List[Dict[str, Union[str, float]]]]:
    try:
        data = json.loads(response_text)

        if "themes" not in data or not isinstance(data["themes"], list):
            logger.warning(f"⚠️ Clé 'themes' manquante ou invalide : {response_text}")
            return None

        results = []
        for item in data["themes"]:
            if not isinstance(item, dict):
                logger.warning(f"⚠️ Élément non structuré : {item}")
                continue

            theme = item.get("theme")
            note = item.get("note")

            if theme not in THEME_LABELS:
                logger.warning(f"⚠️ Thème inconnu : {theme}")
                continue

            if not isinstance(note, (int, float)) or not (1 <= note <= 5):
                logger.warning(f"⚠️ Note invalide pour {theme} : {note}")
                continue

            results.append({"theme": theme, "note": note})

        return results if results else None

    except json.JSONDecodeError as e:
        logger.error(f"❌ Erreur JSON : {e} dans : {response_text}")
        raise ValueError("Réponse Claude invalide")
