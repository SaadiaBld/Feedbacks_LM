import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import uuid
import time
import random
import os
import csv

def scrape_reviews(mode='json', output_path='data/avis_boutique.csv'):
    """
    Scrape les avis Trustpilot de Leroy Merlin datant de moins de 7 jours.
    
    - mode='csv' => écrit dans un fichier CSV
    - mode='json' => retourne une liste de dictionnaires
    """

    seven_days_ago = datetime.utcnow().date() - timedelta(days=7)
    scrape_date = datetime.utcnow().date().isoformat()

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"
    }

    BASE_URL = "https://fr.trustpilot.com"
    START_URL = "https://fr.trustpilot.com/review/www.leroymerlin.fr"
    current_url = START_URL

    all_reviews = []

    # Si mode CSV : prépare le fichier
    if mode == 'csv':
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        file = open(output_path, mode='w', newline='', encoding='utf-8')
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(['review_id', 'rating', 'comment', 'author', 'publication_date', 'scrape_date'])

    while current_url:
        print(f"Scraping : {current_url}")
        try:
            response = requests.get(current_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Erreur : {e}")
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
            span_name = review.find("span", attrs={"data-consumer-name-typography": "true"})
            author = span_name.text.strip() if span_name else "Auteur inconnu"

            # Date de publication
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

            review_id = str(uuid.uuid4())

            review_data = {
                "review_id": review_id,
                "rating": int(rating),
                "comment": comment,
                "author": author,
                "publication_date": publication_date.isoformat(),
                "scrape_date": scrape_date
            }

            if mode == 'csv':
                writer.writerow(review_data.values())
            else:
                all_reviews.append(review_data)

        if stop_scraping:
            break

        next_page_tag = soup.find('a', attrs={"aria-label": "Page suivante"})
        current_url = BASE_URL + next_page_tag['href'] if next_page_tag else None

        time.sleep(random.uniform(2, 4))

    if mode == 'csv':
        file.close()
        print(f"Scraping terminé. Données enregistrées dans {output_path}")
    else:
        return all_reviews
    
#si on execute le fichier en tant que script python app/scraper.py
if __name__ == "__main__":
    scrape_reviews(mode='csv')