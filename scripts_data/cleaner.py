import pandas as pd
import re
import os
from datetime import datetime

def clean_emojis(text):
    # Suppression simple d'emojis (exemple générique, à adapter si tu veux plus précis)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticônes
        "\U0001F300-\U0001F5FF"  # symboles et pictogrammes
        "\U0001F680-\U0001F6FF"  # transports et cartes
        "\U0001F1E0-\U0001F1FF"  # drapeaux (iOS)
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def clean_text(text):
    if pd.isna(text):
        return ""
    # Supprime emojis
    text = clean_emojis(text)
    # Supprime les espaces multiples et sauts de ligne
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def clean_csv(input_file, output_file):
    # Charger le CSV
    df = pd.read_csv(input_file, dtype=str)
    
    # Vérification du nombre de colonnes
    expected_cols = ['review_id', 'rating', 'content', 'author', 'publication_date', 'scrape_date']
    if list(df.columns) != expected_cols:
        raise ValueError(f"Le fichier CSV a une structure invalide : {list(df.columns)}. Attendu : {expected_cols}")
    # Nettoyer les commentaires
    df['content'] = df['content'].astype(str).apply(clean_text)
    
    # Supprimer les lignes où content est vide ou juste un "?"
    df = df[~df['content'].isin(["?", ""])]
    
    # supprimer les lignes où content est NaN ou vide
    df = df[~df['content'].isna()]
    df = df[df['content'].str.strip() != ""]

    #supprimer les lignes en double pour les champs 'content' et 'author' similaire
    df = df.drop_duplicates(subset=['review_id'], keep='first')
    
    # Sauvegarder le CSV nettoyé
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Fichier nettoyé sauvegardé dans {output_file}")


def clean_data():
    input_file = "data/avis_boutique.csv"
    output_file = "data/avis_boutique_clean.csv"
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} introuvable. Lance d'abord le scraper.")
    clean_csv(input_file, output_file)

