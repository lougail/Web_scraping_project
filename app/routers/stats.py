"""Router FastAPI pour les endpoints de statistiques.

Ce module définit les routes HTTP pour accéder aux statistiques agrégées sur les livres (moyennes, top catégories, etc.).
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.session import get_db
from app.services.book_service import BookService
from app.schemas.book import CategoryStats, PriceStats, GeneralStats, RatingDistribution, PriceRange

router = APIRouter(prefix="/stats", tags=["Statistics"])
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Factory pour l'injection de dépendance du service des livres.

    Args:
        db (Session): Session de base de données injectée par FastAPI

    Returns:
        BookService: Instance du service des livres
    """
    return BookService(db)


@router.get("/general", response_model=GeneralStats)
def general_stats(service: BookService = Depends(get_book_service)):
    """Récupère les statistiques générales sur l'ensemble des livres.

    Args:
        service (BookService): Service injecté automatiquement

    Returns:
        GeneralStats: Statistiques générales validées contenant :
            - total_books (int): Nombre total de livres
            - average_price (float): Prix moyen de tous les livres

    Example:
        GET /stats/general
        {
            "total_books": 1000,
            "average_price": 35.50
        }
    """
    return GeneralStats(
        total_books=service.get_total_books(),
        average_price=service.get_average_price(),
    )


@router.get("/top-categories", response_model=List[CategoryStats])
def top_categories(
    limit: int = Query(10, ge=1, le=50, description="Nombre de catégories à retourner"),
    service: BookService = Depends(get_book_service),
):
    """Récupère les catégories avec le plus de livres.

    Args:
        limit (int): Nombre maximum de catégories à retourner (1-50)
        service (BookService): Service injecté automatiquement

    Returns:
        List[CategoryStats]: Liste des catégories triées par nombre de livres décroissant

    Example:
        GET /stats/top-categories?limit=5
        [
            {"category": "Fiction", "count": 150},
            {"category": "Mystery", "count": 120}
        ]
    """
    return service.get_top_categories(limit)


@router.get("/price-by-category", response_model=List[PriceStats])
def price_by_category(service: BookService = Depends(get_book_service)):
    """Calcule le prix moyen des livres par catégorie.

    Args:
        service (BookService): Service injecté automatiquement

    Returns:
        List[PriceStats]: Liste des prix moyens par catégorie,
                         triée par prix décroissant

    Example:
        GET /stats/price-by-category
        [
            {"category": "Art", "avg_price": 45.99},
            {"category": "Science", "avg_price": 39.50}
        ]
    """
    return service.get_price_by_category()


@router.get("/rating-distribution", response_model=List[RatingDistribution])
@limiter.limit("100/minute")
def rating_distribution(
    request: Request,
    service: BookService = Depends(get_book_service)
):
    """Récupère la distribution des notes (1-5 étoiles).

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        service (BookService): Service injecté automatiquement

    Returns:
        List[RatingDistribution]: Distribution des notes avec comptage

    Example:
        GET /stats/rating-distribution
        [
            {"rating": 1, "count": 50},
            {"rating": 2, "count": 120},
            {"rating": 3, "count": 300},
            {"rating": 4, "count": 400},
            {"rating": 5, "count": 130}
        ]
    """
    return service.get_rating_distribution()


@router.get("/price-ranges", response_model=List[PriceRange])
@limiter.limit("100/minute")
def price_ranges(
    request: Request,
    service: BookService = Depends(get_book_service)
):
    """Calcule la distribution des prix par tranches.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        service (BookService): Service injecté automatiquement

    Returns:
        List[PriceRange]: Distribution des livres par tranche de prix

    Example:
        GET /stats/price-ranges
        [
            {"range": "0-10", "count": 150},
            {"range": "10-20", "count": 300},
            {"range": "20-30", "count": 250},
            {"range": "30-40", "count": 180},
            {"range": "40-50", "count": 90},
            {"range": "50+", "count": 30}
        ]
    """
    return service.get_price_ranges()