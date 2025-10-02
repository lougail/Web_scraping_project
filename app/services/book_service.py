from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookResponse, CategoryStats, PriceStats

class BookService:
    """Service pour la logique métier des livres"""
    
    def __init__(self, db: Session):
        self.repo = BookRepository(db)
    
    def list_books(
        self, 
        page: int = 1, 
        per_page: int = 20,
        category: Optional[str] = None
    ) -> List[BookResponse]:
        """Liste paginée de livres"""
        offset = (page - 1) * per_page
        books = self.repo.get_all(offset=offset, limit=per_page, category=category)
        return [BookResponse.model_validate(book) for book in books]
    
    def get_book(self, book_id: int) -> Optional[BookResponse]:
        """Récupérer un livre par ID"""
        book = self.repo.get_by_id(book_id)
        return BookResponse.model_validate(book) if book else None
    
    def get_total_books(self) -> int:
        """Nombre total de livres"""
        return self.repo.count_total()
    
    def get_average_price(self) -> float:
        """Prix moyen de tous les livres"""
        return self.repo.get_average_price()
    
    def get_top_categories(self, limit: int = 10) -> List[CategoryStats]:
        """Top catégories"""
        results = self.repo.get_top_categories(limit)
        return [CategoryStats(**r) for r in results]
    
    def get_price_by_category(self) -> List[PriceStats]:
        """Prix moyen par catégorie"""
        results = self.repo.get_price_by_category()
        return [PriceStats(**r) for r in results]