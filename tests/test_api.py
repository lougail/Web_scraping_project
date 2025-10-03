"""Tests d'intégration pour les endpoints de l'API FastAPI.

Ce module contient les tests fonctionnels qui vérifient le comportement des endpoints de l'API à travers le TestClient de FastAPI.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_books():
    """Test de l'endpoint GET /books - Liste des livres.

    Vérifie que l'endpoint retourne une réponse paginée avec les champs requis.
    """
    r = client.get("/books")
    assert r.status_code == 200
    data = r.json()
    # Nouveau format: réponse paginée
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data
    assert isinstance(data["items"], list)
    if data["items"]:
        book = data["items"][0]
        assert "title" in book
        assert "price" in book
        assert "category" in book


def test_books_pagination():
    """Test de la pagination sur GET /books.

    Vérifie que le paramètre per_page limite correctement le nombre de résultats.
    """
    r = client.get("/books?page=1&per_page=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) <= 5
    assert data["per_page"] == 5
    assert data["page"] == 1


def test_books_filter_category():
    """Test du filtrage par catégorie sur GET /books.

    Vérifie que seuls les livres de la catégorie demandée sont retournés.
    """
    r = client.get("/books?category=Fiction")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    for book in data["items"]:
        assert book["category"] == "Fiction"


def test_book_detail_valid():
    """Test de l'endpoint GET /books/{id} avec un ID valide.

    Vérifie que les détails d'un livre sont correctement retournés.
    """
    r = client.get("/books/1")
    if r.status_code == 200:
        data = r.json()
        assert "title" in data
        assert "price" in data


def test_book_detail_not_found():
    """Test de l'endpoint GET /books/{id} avec un ID inexistant.

    Vérifie que l'API retourne une erreur 404 pour un livre inexistant.
    """
    r = client.get("/books/999999")
    assert r.status_code == 404


def test_stats_general():
    """Test de l'endpoint GET /stats/general.

    Vérifie que les statistiques générales sont retournées correctement.
    """
    r = client.get("/stats/general")
    assert r.status_code == 200
    assert "average_price" in r.json()


def test_stats_top_categories():
    """Test de l'endpoint GET /stats/top-categories.

    Vérifie que le top des catégories est retourné sous forme de liste.
    """
    r = client.get("/stats/top-categories")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_stats_price_by_category():
    """Test de l'endpoint GET /stats/price-by-category.

    Vérifie que les prix moyens par catégorie sont retournés.
    """
    r = client.get("/stats/price-by-category")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_root_health():
    """Test des endpoints de base (root et health check).

    Vérifie que les endpoints / et /health répondent correctement.
    """
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
