import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time
import random
import os

scrape_date = datetime.utcnow().date().isoformat()  # Date du jour au format ISO

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}

BASE_URL = "https://fr.trustpilot.com"
START_URL = "https://fr.trustpilot.com/review/www.leroymerlin.fr"  # Commencer directement à la page 11

# Fichier pour sauvegarder l'URL de la dernière page scrappée
LAST_PAGE_FILE = "last_page.txt"

# Fonction pour lire l'URL de la dernière page scrappée
def read_last_page():
    if os.path.exists(LAST_PAGE_FILE) and os.path.getsize(LAST_PAGE_FILE) > 0:
        with open(LAST_PAGE_FILE, "r") as f:
            return f.read().strip()
    return START_URL  # Si pas de fichier ou si vide, commencer depuis la page 11

# Fonction pour sauvegarder l'URL de la dernière page scrappée
def save_last_page(url):
    with open(LAST_PAGE_FILE, "w") as f:
        f.write(url)

# Préparer le fichier CSV en mode ajout (mode 'a')
with open('avis_boutique.csv', mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Si le fichier est vide, ajouter les en-têtes (sinon, ne pas les ajouter)
    if file.tell() == 0:
        writer.writerow(['rating', 'content', 'author', 'publication_date', 'scrape_date'])

    current_url = read_last_page()  # Commencer à partir de la dernière page enregistrée ou page 11

    while current_url:
        print(f"Scraping de la page : {current_url}...")
        response = requests.get(current_url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")

        # --- Extraire tous les avis sur la page ---
        reviews = soup.find_all('article', attrs={"data-service-review-card-paper": "true"})

        for review in reviews:
            # 1. Note (étoiles)
            rating_tag = review.find('div', attrs={"data-service-review-rating": True})
            rating = rating_tag['data-service-review-rating'] if rating_tag else "?"

            # 2. Commentaire
            comment_tag = review.find('p', attrs={"data-service-review-text-typography": "true"})
            comment = comment_tag.get_text(separator="\n").strip() if comment_tag else "?"

            # 4. Auteur 
            author = "Auteur inconnu"
            aside = review.find("aside", class_="styles_consumerInfoWrapper_6HM50")
            if aside:
                name_tag = aside.find("span", class_="typography_heading-xs__OsR6")
                if name_tag:
                    author = name_tag.get_text(strip=True)


            # 3. Date de publication
            date_tag = review.find('time')
            date = date_tag['datetime'] if date_tag else "?"

            # 4. Sauvegarder en CSV
            writer.writerow([
                rating,
                comment,
                date,
                scrape_date
            ])

        # --- Trouver le lien de la page suivante ---
        next_page_tag = soup.find('a', attrs={"aria-label": "Page suivante"})
        if next_page_tag:
            # Extraire l'URL complète de la page suivante
            next_page_url = BASE_URL + next_page_tag['href']
            current_url = next_page_url

            # Sauvegarder l'URL de la page actuelle pour la reprise
            save_last_page(current_url)
        else:
            # Si aucune page suivante, arrêter le scraping
            print("Pas de page suivante, fin du scraping.")
            current_url = None

        # Pause aléatoire pour éviter d'être bloqué
        time.sleep(random.uniform(2, 5))

    print("Scraping terminé.")
