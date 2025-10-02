from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.book_service import BookService
from app.schemas.book import CategoryStats, PriceStats

router = APIRouter(prefix="/stats", tags=["Statistics"])

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(db)

@router.get("/general")
def general_stats(service: BookService = Depends(get_book_service)):
    """Statistiques générales"""
    return {
        "total_books": service.get_total_books(),
        "average_price": service.get_average_price()
    }

@router.get("/top-categories", response_model=List[CategoryStats])
def top_categories(
    limit: int = Query(10, ge=1, le=50),
    service: BookService = Depends(get_book_service)
):
    """Top catégories par nombre de livres"""
    return service.get_top_categories(limit)

@router.get("/price-by-category", response_model=List[PriceStats])
def price_by_category(service: BookService = Depends(get_book_service)):
    """Prix moyen par catégorie"""
    return service.get_price_by_category()