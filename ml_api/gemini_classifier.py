"""Ce script effectue avec clé api
  * Lecture des verbatims depuis BigQuery
	* Appel à Gemini pour classer en thèmes
	* Appel à Gemini pour attribuer un score d’insatisfaction
	* Insertion dans une nouvelle table BigQuery
"""
from google.cloud import aiplatform
from vertexai.language_models import TextGenerationModel
import vertexai
from google import genai

client = genai.Client(
    vertexai=True, 
    project='gemini-nlp-test', 
    location='us-central1'
)
vertexai.init(project="gemini-nlp-test", location="us-central1")
model = TextGenerationModel.from_pretrained("text-bison@001")

verbatim = "J'ai commandé une baignoire chez Leroy Merlin, elle est arrivée en retard et en plus elle était cassée. Le service client ne m'a pas aidé, je suis très déçu."

prompt = f"""
Tu es un assistant d'analyse de satisfaction client. Voici un avis client :

"{verbatim}"

Donne les 1 à 3 grands thèmes évoqués dans ce texte (comme livraison, produit, service client, etc.), 
et attribue à chacun un score d’insatisfaction entre 0 et 10, au format JSON compact :
[
  {{
    "theme": "nom_du_theme",
    "score": note_sur_10
  }}
]
"""

response = client.models.generate_content(
    model='gemini-2.0-flash-exp', contents=prompt
)
print(response.text)
