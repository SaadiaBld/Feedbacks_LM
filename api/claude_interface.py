import anthropic
import os
import json
import logging
from dotenv import load_dotenv
from pathlib import Path
from .prompt_utils import build_prompt, THEMES

# Load .env
env_path = Path(__file__).resolve().parents[1] / ".env"
#load_dotenv(dotenv_path=env_path)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)
THEME_LABELS = {t["nom"] for t in THEMES}

# Log setup
logger = logging.getLogger("claude_logger")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.hasHandlers():
    handler = logging.FileHandler("claude_errors.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# def classify_with_claude(verbatim: str) -> dict | None:
#     prompt = build_prompt(verbatim)
#     try:
#         response = client.messages.create(
#             model="claude-3-haiku-20240307",
#             max_tokens=500,
#             temperature=0,
#             system="Tu es un assistant d’analyse de satisfaction client.",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         content = response.content[0].text.strip()
#         validated = validate_claude_response(content)

#         if not validated:
#             logger.warning(f"Réponse non valide : {content}")
#         return validated

#     except Exception as e:
#         logger.error(f"Erreur API Claude : {e}")
#         return None


def classify_with_claude(verbatim: str) -> list[dict] | None:
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
        
        # 🔍 Print brut de la réponse JSON
        print("\n📥 Réponse brute de Claude :\n", content)

        validated = validate_claude_response(content)
        if not validated:
            logger.warning(f"Réponse non valide : {content}")
        return validated

    except Exception as e:
        logger.error(f"Erreur API Claude : {e}")
        return None



def validate_claude_response(response_text: str) -> list[dict] | None:
    try:
        data = json.loads(response_text)

        if "themes" not in data or not isinstance(data["themes"], list):
            logger.warning(f"Clé 'themes' manquante ou invalide dans : {response_text}")
            return None

        results = []

        for item in data["themes"]:
            if not isinstance(item, dict):
                logger.warning(f"Item non structuré correctement : {item}")
                continue

            theme = item.get("theme")
            note = item.get("note")

            if theme not in THEME_LABELS:
                logger.warning(f"Thème inconnu : {theme}")
                continue

            if not isinstance(note, (int, float)) or not (1 <= note <= 5):
                logger.warning(f"Note invalide pour {theme} : {note}")
                continue

            results.append({"theme": theme, "note": note})

        return results if results else None

    except json.JSONDecodeError as e:
        logger.error(f"Erreur JSON : {e} dans : {response_text}")
        return None

