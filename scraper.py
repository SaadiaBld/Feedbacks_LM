# Scraper les avis de Leroy Merlin sur Trustpilot datant de moins de 7 jours

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import time
import uuid
import random
import os

def scrape_reviews():
    """
    Scrape reviews from Leroy Merlin's Trustpilot page that are less than 7 days old.
    The results are saved in a CSV file.
    """

    # Date d’aujourd’hui et seuil de 7 jours
    scrape_date = datetime.utcnow().date().isoformat()
    seven_days_ago = datetime.utcnow().date() - timedelta(days=7)

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"
                    }
    BASE_URL = "https://fr.trustpilot.com"
    START_URL = "https://fr.trustpilot.com/review/www.leroymerlin.fr"
    # Créer le dossier si nécessaire
    os.makedirs("data", exist_ok=True)

    # Préparer le CSV
    with open('data/avis_boutique.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)

        # Écrire l'en-tête si le fichier est vide
        if file.tell() == 0:
            writer.writerow(['review_id', 'rating', 'content', 'author', 'publication_date', 'scrape_date'])

        current_url = START_URL

        while current_url:
            print(f"Scraping de la page : {current_url}")
            try:
                response = requests.get(current_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                response.encoding = 'utf-8'
            except requests.RequestException as e:
                print(f"Erreur lors de la requête : {e}")
                break

            soup = BeautifulSoup(response.content, "html.parser")
            reviews = soup.find_all('article', attrs={"data-service-review-card-paper": "true"})

            stop_scraping = False

            for review in reviews:
                # Note
                rating_tag = review.find('div', attrs={"data-service-review-rating": True})
                rating = rating_tag['data-service-review-rating'] if rating_tag else None

                # Commentaire
                comment_tag = review.find('p', attrs={"data-service-review-text-typography": True})
                if comment_tag:
                    for br in comment_tag.find_all("br"):
                        br.replace_with("\n")
                    comment = comment_tag.get_text(separator="\n").strip()
                else:
                    comment = None

                # Auteur
                author = None

                # 1. Format courant
                span_name = review.find("span", attrs={"data-consumer-name-typography": "true"})
                if span_name:
                    author = span_name.text.strip()

                # 2. Fallback si nom absent
                if not author:
                    aside = review.find("aside", class_="styles_consumerInfoWrapper_6HM50")
                    if aside:
                        name_tag = aside.find("span", class_="typography_heading-xs__OsR6")
                        if name_tag:
                            author = name_tag.get_text(strip=True)

                # 3. Par défaut si aucun nom trouvé
                if not author:
                    author = "Auteur inconnu"

                # Date
                date_tag = review.find('time')
                if date_tag and date_tag.has_attr('datetime'):
                    try:
                        publication_date = datetime.fromisoformat(
                            date_tag['datetime'].replace('Z', '+00:00')
                        ).date()
                    except ValueError:
                        continue
                else:
                    publication_date = None

                # Filtres : ignorer si champs manquants ou trop ancien
                if not rating or not comment or not publication_date:
                    continue

                if publication_date < seven_days_ago:
                    stop_scraping = True
                    break

                review_id = str(uuid.uuid4()) # Générer un ID unique pour chaque avis

                # Écrire dans le fichier
                writer.writerow([
                    review_id,
                    rating,
                    comment,
                    author,
                    publication_date.isoformat(),
                    scrape_date
                ])

            if stop_scraping:
                print("Tous les avis restants datent de plus de 7 jours. Fin.")
                break

            # Pagination
            next_page_tag = soup.find('a', attrs={"aria-label": "Page suivante"})
            if next_page_tag:
                next_page_url = BASE_URL + next_page_tag['href']
                current_url = next_page_url
                print(f"Page suivante trouvée : {current_url}")
            else:
                print("Pas de page suivante, fin du scraping.")
                break

            # Pause aléatoire
            time.sleep(random.uniform(2, 5))

    print("Scraping terminé.")