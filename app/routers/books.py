from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.services.book_service import BookService
from app.schemas.book import BookResponse
from app.config import settings

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Dependency injection du service"""
    return BookService(db)

@router.get("", response_model=List[BookResponse])
def list_books(
    page: int = Query(1, ge=1, description="Numéro de page"),
    per_page: int = Query(settings.PAGINATION_DEFAULT, ge=1, le=settings.PAGINATION_MAX),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    service: BookService = Depends(get_book_service)
):
    """Liste des livres avec pagination et filtres"""
    return service.list_books(page=page, per_page=per_page, category=category)

@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    service: BookService = Depends(get_book_service)
):
    """Détails d'un livre"""
    book = service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book