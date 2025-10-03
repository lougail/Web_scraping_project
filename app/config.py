"""Module de configuration centralisée de l'application.

Ce module définit les paramètres de configuration de l'API via Pydantic Settings, permettant de charger les valeurs depuis des variables d'environnement ou un fichier .env.

Attributes:
    BASE_DIR (Path): Répertoire racine du projet
    SCRAPY_PROJECT_DIR (Path): Répertoire du projet Scrapy
    DB_PATH (Path): Chemin vers la base de données SQLite
    settings (Settings): Instance singleton des paramètres de configuration
"""

from pathlib import Path
from pydantic_settings import BaseSettings

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
SCRAPY_PROJECT_DIR = BASE_DIR / "books_scraper"
DB_PATH = SCRAPY_PROJECT_DIR / "books.db"


class Settings(BaseSettings):
    """Configuration centralisée de l'application FastAPI.

    Utilise Pydantic Settings pour la validation et le chargement des variables d'environnement. Les valeurs peuvent être surchargées via un fichier .env.

    Attributes:
        APP_NAME (str): Nom de l'application affiché dans la documentation
        VERSION (str): Version de l'API (format semver)
        DEBUG (bool): Active le mode debug (logs SQL, etc.)
        DATABASE_URL (str): URL de connexion à la base de données SQLite
        PAGINATION_DEFAULT (int): Nombre d'éléments par page par défaut
        PAGINATION_MAX (int): Nombre maximum d'éléments par page autorisé

    Example:
        >>> from app.config import settings
        >>> print(settings.DATABASE_URL)
        sqlite:///c:/path/to/books.db
    """

    # Application
    APP_NAME: str = "Books Competitive Intelligence API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"

    # Pagination
    PAGINATION_DEFAULT: int = 20
    PAGINATION_MAX: int = 100

    class Config:
        """Configuration Pydantic."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()
