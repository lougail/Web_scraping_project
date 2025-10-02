import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent
BOOKS_SCRAPER_DIR = BASE_DIR / "books_scraper"
DB_PATH = BOOKS_SCRAPER_DIR / "books.db"

# Base de données
DATABASE_URL = f"sqlite:///{DB_PATH}"

# API
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))