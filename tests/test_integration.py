import sqlite3
from fastapi.testclient import TestClient
from app.main import app

def test_full_scraping_to_api():
    # Vérifie qu'au moins 1 livre scrapé est accessible via l'API (suppose que scraping a été lancé)
    conn = sqlite3.connect("books_scraper/books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM books LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    book_id = row[0]
    client = TestClient(app)
    r = client.get(f"/books/{book_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == book_id