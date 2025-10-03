"""Router FastAPI pour les endpoints d'historique des livres.

Ce module définit les routes HTTP pour accéder à l'historique des modifications des livres (prix, stock, rating, reviews).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.session import get_db
from app.services.book_service import BookService
from app.schemas.book import BookHistoryEntry, PriceEvolution, PriceChange

router = APIRouter(prefix="/history", tags=["History"])
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Factory pour l'injection de dépendance du service des livres.

    Args:
        db (Session): Session de base de données injectée par FastAPI

    Returns:
        BookService: Instance du service des livres
    """
    return BookService(db)


@router.get("/books/{book_id}", response_model=List[BookHistoryEntry])
@limiter.limit("100/minute")
def get_book_history(
    request: Request,
    book_id: int,
    days: Optional[int] = Query(None, ge=1, le=365, description="Limiter aux N derniers jours"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Nombre max d'entrées"),
    service: BookService = Depends(get_book_service),
):
    """Récupère l'historique complet d'un livre.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        book_id (int): Identifiant du livre
        days (Optional[int]): Limiter aux N derniers jours (1-365)
        limit (Optional[int]): Nombre maximum d'entrées (1-1000)
        service (BookService): Service injecté automatiquement

    Returns:
        List[BookHistoryEntry]: Historique complet du livre

    Raises:
        HTTPException: 404 si le livre n'existe pas

    Example:
        GET /history/books/1?days=30&limit=100
    """
    # Vérifier que le livre existe
    book = service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    history = service.get_book_history(book_id, days, limit)
    return history


@router.get("/books/{book_id}/price", response_model=List[PriceEvolution])
@limiter.limit("100/minute")
def get_price_history(
    request: Request,
    book_id: int,
    days: Optional[int] = Query(None, ge=1, le=365, description="Limiter aux N derniers jours"),
    service: BookService = Depends(get_book_service),
):
    """Récupère l'évolution des prix d'un livre.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        book_id (int): Identifiant du livre
        days (Optional[int]): Limiter aux N derniers jours (1-365)
        service (BookService): Service injecté automatiquement

    Returns:
        List[PriceEvolution]: Évolution des prix avec dates

    Raises:
        HTTPException: 404 si le livre n'existe pas

    Example:
        GET /history/books/1/price?days=7
        [
            {"date": "2025-09-26T10:00:00", "price": 25.99},
            {"date": "2025-10-03T10:00:00", "price": 19.99}
        ]
    """
    # Vérifier que le livre existe
    book = service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    price_history = service.get_price_history(book_id, days)
    return price_history


@router.get("/price-changes", response_model=List[PriceChange])
@limiter.limit("50/minute")
def get_recent_price_changes(
    request: Request,
    days: int = Query(7, ge=1, le=90, description="Nombre de jours à analyser"),
    limit: int = Query(50, ge=1, le=200, description="Nombre max de résultats"),
    service: BookService = Depends(get_book_service),
):
    """Récupère les livres dont le prix a changé récemment.

    Endpoint très utile pour la veille concurrentielle : permet de détecter rapidement les promotions, hausses de prix, etc.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        days (int): Nombre de jours à analyser (1-90, défaut: 7)
        limit (int): Nombre maximum de résultats (1-200, défaut: 50)
        service (BookService): Service injecté automatiquement

    Returns:
        List[PriceChange]: Liste des changements de prix détectés

    Example:
        GET /history/price-changes?days=7&limit=20
        [
            {
                "book_id": 42,
                "upc": "abc123",
                "title": "Clean Code",
                "old_price": 30.0,
                "new_price": 25.0,
                "change_percent": -16.67,
                "changed_at": "2025-10-01T12:00:00"
            }
        ]
    """
    changes = service.get_recent_price_changes(days, limit)
    return changes


@router.get("/stock-alerts")
@limiter.limit("100/minute")
def get_stock_alerts(
    request: Request,
    threshold: int = Query(10, ge=0, le=100, description="Seuil de stock faible"),
    service: BookService = Depends(get_book_service),
):
    """Récupère les livres avec un stock faible ou en rupture.

    Endpoint pour surveiller les ruptures de stock et anticiper les réapprovisionnements.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        threshold (int): Seuil de stock faible (0-100, défaut: 10)
        service (BookService): Service injecté automatiquement

    Returns:
        List[dict]: Liste des livres en stock faible

    Example:
        GET /history/stock-alerts?threshold=5
        [
            {
                "book_id": 1,
                "upc": "abc123",
                "title": "Python Crash Course",
                "current_stock": 3,
                "last_checked": "2025-10-03T10:00:00",
                "status": "low_stock"
            },
            {
                "book_id": 2,
                "upc": "xyz789",
                "title": "Clean Code",
                "current_stock": 0,
                "last_checked": "2025-10-03T10:00:00",
                "status": "out_of_stock"
            }
        ]
    """
    alerts = service.get_stock_alerts(threshold)
    return alerts
