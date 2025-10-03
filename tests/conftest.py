"""Configuration globale et fixtures pytest pour les tests.

Ce module contient les fixtures réutilisables pour les tests, notamment pour la gestion des sessions de base de données.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.database.models import Book


@pytest.fixture(scope="function")
def test_db_session():
    """Fixture pour créer une session de base de données de test en mémoire.

    Cette fixture crée une base de données SQLite en mémoire pour chaque test, garantissant l'isolation des tests.

    Yields:
        Session: Session SQLAlchemy de test

    Example:
        >>> def test_something(test_db_session):
        ...     service = BookService(test_db_session)
        ...     result = service.get_total_books()
    """
    # Créer un moteur de base de données en mémoire
    engine = create_engine("sqlite:///:memory:")

    # Créer toutes les tables
    Base.metadata.create_all(engine)

    # Créer une session factory
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Créer une session
    session = TestSessionLocal()

    # Retourner la session pour le test
    yield session

    # Cleanup : fermer la session et supprimer les tables
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session():
    """Fixture pour créer une session de base de données de développement.

    Utilise la base de données de développement existante (books.db).
    À utiliser pour les tests d'intégration qui nécessitent des données réelles.

    Yields:
        Session: Session SQLAlchemy sur la DB de développement

    Example:
        >>> def test_with_real_data(db_session):
        ...     service = BookService(db_session)
        ...     books = service.list_books(page=1, per_page=5)
    """
    from books_scraper.database.connection import SessionLocal

    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def sample_book_data():
    """Fixture fournissant des données de test pour un livre.

    Returns:
        dict: Dictionnaire contenant les données d'un livre de test

    Example:
        >>> def test_create_book(test_db_session, sample_book_data):
        ...     book = Book(**sample_book_data)
        ...     test_db_session.add(book)
        ...     test_db_session.commit()
    """
    return {
        "upc": "test123456",
        "title": "Test Book",
        "price": 29.99,
        "rating": 5,
        "stock": 10,
        "category": "Fiction",
        "description": "A test book description",
        "number_of_reviews": 42,
        "cover": "http://example.com/cover.jpg",
        "product_type": "Books",
    }
