from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

# Ajouter le chemin racine
root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from books_scraper.database.connection import SessionLocal
from books_scraper.database.models import Book
from books_scraper.database.queries import (
    get_average_price,
    get_top_categories,
    get_average_price_by_category
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class BookResponse(BaseModel):
    id: int
    title: str
    price: float
    rating: Optional[int]
    category: Optional[str]
    stock: Optional[int]
    
    class Config:
        from_attributes = True

# App
app = FastAPI(
    title="Books API",
    description="API de veille concurrentielle",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Books API", "docs": "/docs"}

@app.get("/books", response_model=List[BookResponse])
def get_books(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * per_page
    books = db.query(Book).offset(offset).limit(per_page).all()
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book

@app.get("/stats/average-price")
def average_price():
    return {"average_price": get_average_price()}

@app.get("/stats/top-categories")
def top_categories(limit: int = 10):
    return get_top_categories(limit)

@app.get("/stats/price-by-category")
def price_by_category():
    return get_average_price_by_category()