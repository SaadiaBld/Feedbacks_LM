# Scraper les avis de Leroy Merlin sur Trustpilot datant de moins de 7 jours

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv, time, uuid, random, os
import pandas as pd

def scrape_reviews(mode = "csv"):
    """
    Scrape les avis Trustpilot de Leroy Merlin datant de moins de 7 jours.
    Modes possibles :
    - 'csv' : sauvegarde dans un fichier CSV
    - 'json' : retourne une liste de dictionnaires (pour l’API)
    - 'pandas' : retourne un DataFrame (pour un pipeline NLP)
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

    reviews_list = []
    current_url = START_URL

    while current_url:
        print(f"Scraping : {current_url}")
        try:
            response = requests.get(current_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
        except requests.RequestException as e:
            print(f"Erreur HTTP : {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        reviews = soup.find_all('article', attrs={"data-service-review-card-paper": "true"})
        stop_scraping = False

        for review in reviews:
            rating_tag = review.find('div', attrs={"data-service-review-rating": True})
            rating = rating_tag['data-service-review-rating'] if rating_tag else None

            comment_tag = review.find('p', attrs={"data-service-review-text-typography": True})
            if comment_tag:
                for br in comment_tag.find_all("br"):
                    br.replace_with("\n")
                comment = comment_tag.get_text(separator="\n").strip()
            else:
                comment = None

            author = review.find("span", attrs={"data-consumer-name-typography": "true"})
            author = author.text.strip() if author else "Auteur inconnu"

            date_tag = review.find('time')
            if date_tag and date_tag.has_attr('datetime'):
                try:
                    publication_date = datetime.fromisoformat(date_tag['datetime'].replace('Z', '+00:00')).date()
                except ValueError:
                    continue
            else:
                publication_date = None

            if not rating or not comment or not publication_date:
                continue
            if publication_date < seven_days_ago:
                stop_scraping = True
                break

            review_dict = {
                'review_id': str(uuid.uuid4()),
                'rating': rating,
                'content': comment,
                'author': author,
                'publication_date': publication_date.isoformat(),
                'scrape_date': scrape_date
            }

            reviews_list.append(review_dict)

        if stop_scraping:
            print("Tous les avis restants datent de plus de 7 jours. Fin.")
            break

        next_page_tag = soup.find('a', attrs={"aria-label": "Page suivante"})
        current_url = BASE_URL + next_page_tag['href'] if next_page_tag else None

        time.sleep(random.uniform(2, 5))

    print("Scraping terminé.")

    # === Sortie selon le mode ===
    if mode == "json":
        return reviews_list
    elif mode == "pandas":
        return pd.DataFrame(reviews_list)
    else:  # mode == "csv"
        with open('data/avis_boutique.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['review_id', 'rating', 'content', 'author', 'publication_date', 'scrape_date'], quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for review in reviews_list:
                writer.writerow(review)