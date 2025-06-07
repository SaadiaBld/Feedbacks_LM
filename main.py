#fichier qui va lancer le scraping, le nettoyage et stockage en csv

from scraper import scrape_reviews
from cleaner import clean_csv
from datetime import datetime

# Lancer le scraping
def main():
    print(f"Début du scraping à {datetime.now().isoformat()}")
    scrape_reviews()
    print(f"Fin du scraping à {datetime.now().isoformat()}")
    # Nettoyer le CSV
    print(f"Début du nettoyage à {datetime.now().isoformat()}")
    input_file = 'data/avis_boutique.csv'
    output_file = 'data/avis_nettoyes.csv'
    clean_csv(input_file, output_file)
    print(f"Fin du nettoyage à {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
    print("Script terminé avec succès.")

