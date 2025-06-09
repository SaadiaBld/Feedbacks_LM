"""Ce script effectue:
    * Lecture des verbatims depuis BigQuery
	* Appel à Gemini pour classer en thèmes
	* Appel à Gemini pour attribuer un score d’insatisfaction
	* Insertion dans une nouvelle table BigQuery
"""

import vertexai
from vertexai.language_models import TextGenerationModel

# Initialise Vertex AI avec ton projet et la région
vertexai.init(project="trustpilot-satisfaction", location="europe-west1")

# Charge le modèle Gemini
model = TextGenerationModel.from_pretrained("gemini-2.0-flash")

# Exemple de verbatim client
verbatim = """
J'ai commandé une baignoire chez Leroy Merlin, elle est arrivée en retard et en plus elle était cassée. 
Le service client ne m'a pas aidé, je suis très déçu.
"""

# Prompt à personnaliser selon ta taxonomie de thèmes
prompt = f"""
Tu es un assistant d'analyse de satisfaction client. Voici un avis client :

"{verbatim}"

Donne les 1 à 3 grands thèmes évoqués dans ce texte (comme livraison, produit, service client, etc.), 
et attribue à chacun un score d’insatisfaction entre 0 (satisfait) et 10 (très insatisfait), au format JSON compact :
[
  {{
    "theme": "nom_du_theme",
    "score": note_sur_10
  }}
]
"""

# Envoie du prompt à Gemini
response = model.predict(prompt=prompt, temperature=0.2, max_output_tokens=256)

# Affiche la réponse
print("Réponse Gemini :\n", response.text)