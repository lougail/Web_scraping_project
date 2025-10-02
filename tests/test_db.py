import sqlite3

def test_db_exists():
    conn = sqlite3.connect("books_scraper/books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    assert "books" in tables
    conn.close()

def test_books_not_empty():
    conn = sqlite3.connect("books_scraper/books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books;")
    count = cursor.fetchone()[0]
    assert count > 0
    conn.close()

def test_books_unique_upc():
    conn = sqlite3.connect("books_scraper/books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT upc, COUNT(*) FROM books GROUP BY upc HAVING COUNT(*) > 1;")
    duplicates = cursor.fetchall()
    assert len(duplicates) == 0
    conn.close()