from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_books():
    r = client.get("/books")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        book = data[0]
        assert "title" in book
        assert "price" in book
        assert "category" in book

def test_books_pagination():
    r = client.get("/books?page=1&per_page=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 5

def test_books_filter_category():
    r = client.get("/books?category=Fiction")
    assert r.status_code == 200
    for book in r.json():
        assert book["category"] == "Fiction"

def test_book_detail_valid():
    r = client.get("/books/1")
    if r.status_code == 200:
        data = r.json()
        assert "title" in data
        assert "price" in data

def test_book_detail_not_found():
    r = client.get("/books/999999")
    assert r.status_code == 404

def test_stats_general():
    r = client.get("/stats/general")
    assert r.status_code == 200
    assert "average_price" in r.json()

def test_stats_top_categories():
    r = client.get("/stats/top-categories")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_stats_price_by_category():
    r = client.get("/stats/price-by-category")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_root_health():
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200