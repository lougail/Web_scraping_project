from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.models import Book

class BookRepository:
    """Repository pour l'accès aux données des livres"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, offset: int = 0, limit: int = 20, category: Optional[str] = None) -> List[Book]:
        """Récupérer une liste de livres avec pagination"""
        query = self.db.query(Book)
        
        if category:
            query = query.filter(Book.category == category)
        
        return query.offset(offset).limit(limit).all()
    
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Récupérer un livre par son ID"""
        return self.db.query(Book).filter(Book.id == book_id).first()
    
    def get_by_upc(self, upc: str) -> Optional[Book]:
        """Récupérer un livre par son UPC"""
        return self.db.query(Book).filter(Book.upc == upc).first()
    
    def count_total(self) -> int:
        """Compter le nombre total de livres"""
        return self.db.query(Book).count()
    
    def get_average_price(self) -> float:
        """Calculer le prix moyen"""
        result = self.db.query(func.avg(Book.price)).scalar()
        return round(result, 2) if result else 0.0
    
    def get_top_categories(self, limit: int = 10) -> List[dict]:
        """Top catégories par nombre de livres"""
        results = self.db.query(
            Book.category,
            func.count(Book.id).label('count')
        ).group_by(Book.category)\
         .order_by(func.count(Book.id).desc())\
         .limit(limit)\
         .all()
        
        return [{'category': r[0], 'count': r[1]} for r in results]
    
    def get_price_by_category(self) -> List[dict]:
        """Prix moyen par catégorie"""
        results = self.db.query(
            Book.category,
            func.avg(Book.price).label('avg_price')
        ).group_by(Book.category)\
         .order_by(func.avg(Book.price).desc())\
         .all()
        
        return [{'category': r[0], 'avg_price': round(r[1], 2)} for r in results]