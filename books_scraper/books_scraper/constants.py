"""Constantes utilisées dans le projet de scraping.

Ce module centralise toutes les constantes et valeurs magiques utilisées dans le scraper pour faciliter la maintenance et les modifications.
"""

# Mapping des notes textuelles vers des valeurs numériques
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}

# URL de base du site scraté
BASE_URL = "http://books.toscrape.com"

# Valeurs par défaut
DEFAULT_RATING = 0
DEFAULT_STOCK = 0
DEFAULT_REVIEWS = 0
