from app.services.book_service import BookService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Remplace le chemin ci-dessous par celui de ta base de test si besoin
engine = create_engine("sqlite:///books_scraper/books.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_get_average_price():
    db = SessionLocal()
    service = BookService(db)
    avg = service.get_average_price()
    assert isinstance(avg, (int, float))
    assert avg >= 0
    db.close()

def test_list_books():
    db = SessionLocal()
    service = BookService(db)
    books = service.list_books(page=1, per_page=5)
    assert isinstance(books, list)
    assert len(books) <= 5
    if books:
        book = books[0]
        assert hasattr(book, "title")
        assert hasattr(book, "price")
        assert hasattr(book, "category")
    db.close()

def test_get_book():
    db = SessionLocal()
    service = BookService(db)
    # On récupère un livre existant si la BDD n'est pas vide
    books = service.list_books(page=1, per_page=1)
    if books:
        book_id = books[0].id
        book = service.get_book(book_id)
        assert book is not None
        assert book.id == book_id
    db.close()

def test_get_top_categories():
    db = SessionLocal()
    service = BookService(db)
    top = service.get_top_categories(limit=3)
    assert isinstance(top, list)
    for cat in top:
        assert hasattr(cat, "category")
        assert hasattr(cat, "count")
    db.close()

def test_get_price_by_category():
    db = SessionLocal()
    service = BookService(db)
    prices = service.get_price_by_category()
    assert isinstance(prices, list)
    for stat in prices:
        assert hasattr(stat, "category")
        assert hasattr(stat, "avg_price")
    db.close()