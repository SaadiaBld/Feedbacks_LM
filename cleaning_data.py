import pandas as pd
import re
from datetime import datetime

def clean_emojis(commentaire):
    '''Supprimer les emojis des commentaires'''
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # émoticônes
        u"\U0001F300-\U0001F5FF"  # symboles & pictogrammes
        u"\U0001F680-\U0001F6FF"  # transport & cartes
        u"\U0001F1E0-\U0001F1FF"  # drapeaux
        u"\U00002700-\U000027BF"  # symboles divers
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    commentaire = emoji_pattern.sub(r'', commentaire)
    commentaire = commentaire.strip()
    commentaire = re.sub(r'\s+', ' ', commentaire)

    return commentaire

def clean_csv(input_file, output_file):
    # Charger le CSV brut
    df = pd.read_csv(input_file)
    
    # Nettoyer les commentaires
    df['Commentaire'] = df['Commentaire'].astype(str).str.strip()  # s'assurer que c'est du texte
    df = df[df['Commentaire'].isin(["?", ""]) == False]  # enlever les lignes vides
    df['Commentaire'] = df['Commentaire'].apply(clean_emojis)  # enlever emojis + espaces
    
    # Harmoniser la date
    def reformat_date(date_raw):
        try:
            date_obj = datetime.strptime(date_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
            return date_obj.strftime("%Y-%m-%d")
        except Exception:
            return ""
    
    df['Date de publication'] = df['Date de publication'].apply(reformat_date)

    # Sauvegarder dans un nouveau CSV nettoyé
    df.to_csv(output_file, index=False)
    print(f"Fichier nettoyé sauvegardé sous {output_file}")

if __name__ == "__main__":
    input_file = 'avis_boutique.csv'
    output_file = 'avis_nettoyes.csv'
    clean_csv(input_file, output_file)
