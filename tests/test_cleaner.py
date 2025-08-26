import os
import pandas as pd
from scripts_data.cleaner import clean_csv

def test_clean_csv_output_structure(tmp_path):
    # Arrange
    input_path = "data/avis_boutique.csv"  # crée un petit fichier de test ici
    output_path = tmp_path / "avis_nettoyes.csv"

    # Act
    clean_csv(input_path, str(output_path))
    df = pd.read_csv(output_path)

    # Assert
    expected_columns = ['review_id', 'rating', 'content', 'author', 'publication_date', 'scrape_date']
    assert list(df.columns) == expected_columns, "Les colonnes nettoyées ne correspondent pas"
    assert not df.isnull().any().any(), "Le fichier nettoyé contient des valeurs nulles"
    assert len(df) > 0, "Le fichier nettoyé est vide"

def test_clean_csv_removes_empty_lines(tmp_path):
    input_path = "data/avis_avec_vides.csv"
    output_path = tmp_path / "avis_clean.csv"

    clean_csv(input_path, str(output_path))
    df = pd.read_csv(output_path)

    assert df['content'].str.strip().ne('').all(), "Des lignes avec contenu vide n'ont pas été supprimées"
