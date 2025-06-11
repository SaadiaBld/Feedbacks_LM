"""Ce script utilise Vertex AI pour analyser un avis client :
    * Classer les thèmes évoqués
    * Attribuer un score d’insatisfaction
"""

import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason


def generate():
    vertexai.init(
        project="trustpilot-satisfaction",
        location="us-central1",
        api_endpoint="us-central1-aiplatform.googleapis.com"
    )
    model = GenerativeModel(
        "gemini-1.5-flash-002", api_version="v1beta1"
    )
    responses = model.generate_content(
        ["De quelle couleur est la banane ?"],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        print(response.text, end="")


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 1,
    "seed": 0,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

generate()