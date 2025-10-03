"""Tests unitaires pour la couche service (BookService).

Ce module teste la logique métier implémentée dans BookService, en interagissant directement avec la base de données de test.
"""

from app.services.book_service import BookService
from app.database.models import Book


def test_get_average_price_empty_db(test_db_session):
    """Test du calcul du prix moyen avec une base de données vide.

    Vérifie que la méthode retourne 0.0 quand il n'y a pas de livres.
    """
    service = BookService(test_db_session)
    avg = service.get_average_price()
    assert isinstance(avg, (int, float))
    assert avg == 0.0


def test_get_average_price_with_data(test_db_session, sample_book_data):
    """Test du calcul du prix moyen avec des données.

    Vérifie que la méthode calcule correctement le prix moyen.
    """
    # Ajouter des livres de test
    book1 = Book(**sample_book_data)
    book2_data = sample_book_data.copy()
    book2_data["upc"] = "test789"
    book2_data["price"] = 10.0
    book2 = Book(**book2_data)

    test_db_session.add(book1)
    test_db_session.add(book2)
    test_db_session.commit()

    service = BookService(test_db_session)
    avg = service.get_average_price()
    assert isinstance(avg, (int, float))
    # Moyenne de 29.99 et 10.0 = 19.995 arrondi à 19.99
    assert avg == 19.99


def test_list_books(test_db_session, sample_book_data):
    """Test de la récupération paginée de livres.

    Vérifie que la liste retournée respecte la limite de pagination et contient les champs attendus.
    """
    # Ajouter un livre de test
    book = Book(**sample_book_data)
    test_db_session.add(book)
    test_db_session.commit()

    service = BookService(test_db_session)
    books = service.list_books(page=1, per_page=5)
    assert isinstance(books, list)
    assert len(books) <= 5
    if books:
        book = books[0]
        assert hasattr(book, "title")
        assert hasattr(book, "price")
        assert hasattr(book, "category")


def test_get_book(test_db_session, sample_book_data):
    """Test de la récupération d'un livre par son ID.

    Vérifie que le service retourne le bon livre quand il existe.
    """
    # Ajouter un livre de test
    book = Book(**sample_book_data)
    test_db_session.add(book)
    test_db_session.commit()

    service = BookService(test_db_session)
    retrieved_book = service.get_book(book.id)
    assert retrieved_book is not None
    assert retrieved_book.id == book.id
    assert retrieved_book.title == sample_book_data["title"]


def test_get_book_not_found(test_db_session):
    """Test de la récupération d'un livre inexistant.

    Vérifie que None est retourné pour un ID inexistant.
    """
    service = BookService(test_db_session)
    book = service.get_book(999999)
    assert book is None


def test_get_top_categories(test_db_session, sample_book_data):
    """Test de la récupération du top des catégories.

    Vérifie que la liste retournée contient les statistiques par catégorie.
    """
    # Ajouter plusieurs livres dans différentes catégories
    book1 = Book(**sample_book_data)
    test_db_session.add(book1)

    book2_data = sample_book_data.copy()
    book2_data["upc"] = "test789"
    book2_data["category"] = "Mystery"
    book2 = Book(**book2_data)
    test_db_session.add(book2)

    test_db_session.commit()

    service = BookService(test_db_session)
    top = service.get_top_categories(limit=3)
    assert isinstance(top, list)
    assert len(top) <= 3
    for cat in top:
        assert hasattr(cat, "category")
        assert hasattr(cat, "count")


def test_get_price_by_category(test_db_session, sample_book_data):
    """Test du calcul des prix moyens par catégorie.

    Vérifie que chaque statistique contient une catégorie et un prix moyen.
    """
    # Ajouter plusieurs livres
    book1 = Book(**sample_book_data)
    test_db_session.add(book1)

    book2_data = sample_book_data.copy()
    book2_data["upc"] = "test789"
    book2_data["price"] = 15.0
    book2 = Book(**book2_data)
    test_db_session.add(book2)

    test_db_session.commit()

    service = BookService(test_db_session)
    prices = service.get_price_by_category()
    assert isinstance(prices, list)
    for stat in prices:
        assert hasattr(stat, "category")
        assert hasattr(stat, "avg_price")


def test_list_books_with_category_filter(test_db_session, sample_book_data):
    """Test du filtrage par catégorie.

    Vérifie que seuls les livres de la catégorie demandée sont retournés.
    """
    # Ajouter des livres dans différentes catégories
    book1 = Book(**sample_book_data)
    test_db_session.add(book1)

    book2_data = sample_book_data.copy()
    book2_data["upc"] = "test789"
    book2_data["category"] = "Mystery"
    book2 = Book(**book2_data)
    test_db_session.add(book2)

    test_db_session.commit()

    service = BookService(test_db_session)
    fiction_books = service.list_books(category="Fiction")
    assert len(fiction_books) == 1
    assert fiction_books[0].category == "Fiction"