import sqlite3

def test_db_exists():
    conn = sqlite3.connect("books_scraper/books.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    assert len(tables) > 0
    conn.close()