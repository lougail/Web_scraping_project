"""Module de configuration de la connexion à la base de données pour Scrapy.

Ce module configure SQLAlchemy pour le projet Scrapy, en créant le moteur de base de données, la classe de base pour les modèles et les fonctions pour gérer les sessions et initialiser la base.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Chemin vers la base de données (dans le répertoire books_scraper)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "books.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Créer le moteur de base de données
engine = create_engine(DATABASE_URL, echo=False)  # echo=False en production

# Classe de base pour les modèles ORM
Base = declarative_base()

# Session factory pour interagir avec la base de données
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Crée et retourne une nouvelle session de base de données.

    Returns:
        Session: Session SQLAlchemy pour les opérations de base de données

    Example:
        >>> session = get_session()
        >>> books = session.query(Book).all()
        >>> session.close()

    Note:
        N'oubliez pas de fermer la session après utilisation.
    """
    return SessionLocal()


def init_db():
    """Initialise la base de données en créant toutes les tables.

    Cette fonction importe tous les modèles et crée les tables correspondantes si elles n'existent pas déjà dans la base de données.

    Example:
        >>> init_db()  # Crée la table books et book_history si elles n'existent pas

    Note:
        Appelé automatiquement au démarrage du spider dans DatabasePipeline.
    """
    from books_scraper.books_scraper.database.models import Book, BookHistory

    Base.metadata.create_all(engine)
