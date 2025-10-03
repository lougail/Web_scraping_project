"""Router FastAPI pour les endpoints relatifs aux livres.

Ce module définit les routes HTTP pour consulter les livres individuellement
ou en liste avec pagination et filtrage.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.session import get_db
from app.services.book_service import BookService
from app.schemas.book import BookResponse, PaginatedResponse
from app.config import settings

router = APIRouter(prefix="/books", tags=["Books"])
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    """Factory pour l'injection de dépendance du service des livres.

    Args:
        db (Session): Session de base de données injectée par FastAPI

    Returns:
        BookService: Instance du service des livres
    """
    return BookService(db)


# Routes spécifiques d'abord (avant /{book_id})

@router.get("/search", response_model=PaginatedResponse[BookResponse])
@limiter.limit("50/minute")
def search_books(
    request: Request,
    q: Optional[str] = Query(None, min_length=2, description="Recherche dans le titre"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    min_price: Optional[float] = Query(None, ge=0, description="Prix minimum"),
    max_price: Optional[float] = Query(None, ge=0, description="Prix maximum"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Note minimum (1-5)"),
    max_rating: Optional[int] = Query(None, ge=1, le=5, description="Note maximum (1-5)"),
    sort_by: str = Query("id", description="Champ de tri (id, title, price, rating)"),
    order: str = Query("asc", description="Ordre de tri (asc, desc)"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    per_page: int = Query(settings.PAGINATION_DEFAULT, ge=1, le=settings.PAGINATION_MAX),
    service: BookService = Depends(get_book_service),
):
    """Recherche de livres avec filtres multi-critères.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        q (Optional[str]): Terme de recherche dans le titre
        category (Optional[str]): Filtre par catégorie
        min_price (Optional[float]): Prix minimum en livres sterling
        max_price (Optional[float]): Prix maximum en livres sterling
        min_rating (Optional[int]): Note minimum (1-5 étoiles)
        max_rating (Optional[int]): Note maximum (1-5 étoiles)
        sort_by (str): Champ de tri (id, title, price, rating)
        order (str): Ordre de tri (asc, desc)
        page (int): Numéro de page
        per_page (int): Nombre de livres par page
        service (BookService): Service injecté automatiquement

    Returns:
        PaginatedResponse[BookResponse]: Résultats paginés avec métadonnées

    Example:
        GET /books/search?q=python&min_price=10&max_price=50&sort_by=price&order=asc
    """
    # Validation: max_price >= min_price
    if min_price and max_price and max_price < min_price:
        raise HTTPException(
            status_code=422,
            detail="max_price doit être supérieur ou égal à min_price"
        )

    # Validation: max_rating >= min_rating
    if min_rating and max_rating and max_rating < min_rating:
        raise HTTPException(
            status_code=422,
            detail="max_rating doit être supérieur ou égal à min_rating"
        )

    # Validation: sort_by valide
    valid_sort_fields = ["id", "title", "price", "rating"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=422,
            detail=f"sort_by doit être l'un de : {', '.join(valid_sort_fields)}"
        )

    # Validation: order valide
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=422,
            detail="order doit être 'asc' ou 'desc'"
        )

    return service.search_books(
        query=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        max_rating=max_rating,
        sort_by=sort_by,
        order=order,
        page=page,
        per_page=per_page,
    )


@router.get("/categories", response_model=List[str])
@limiter.limit("100/minute")
def list_categories(request: Request, service: BookService = Depends(get_book_service)):
    """Récupère la liste de toutes les catégories uniques.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        service (BookService): Service injecté automatiquement

    Returns:
        List[str]: Liste des catégories triées alphabétiquement

    Example:
        GET /books/categories
        ["Fiction", "Mystery", "Science", ...]
    """
    return service.get_categories()


@router.get("/random", response_model=List[BookResponse])
@limiter.limit("100/minute")
def random_books(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Nombre de livres à retourner"),
    service: BookService = Depends(get_book_service),
):
    """Récupère des livres aléatoires.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        limit (int): Nombre de livres à retourner (1-50)
        service (BookService): Service injecté automatiquement

    Returns:
        List[BookResponse]: Liste de livres aléatoires

    Example:
        GET /books/random?limit=5
    """
    return service.get_random_books(limit)


@router.get("/count")
@limiter.limit("100/minute")
def count_books(
    request: Request,
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    service: BookService = Depends(get_book_service),
):
    """Compte le nombre total de livres (avec filtre optionnel).

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        category (Optional[str]): Filtre par catégorie si fourni
        service (BookService): Service injecté automatiquement

    Returns:
        dict: Dictionnaire avec le nombre total de livres

    Example:
        GET /books/count
        {"count": 1000}

        GET /books/count?category=Fiction
        {"count": 150}
    """
    count = service.get_total_books(category=category)
    return {"count": count}


# Routes génériques (liste et détail)

@router.get("", response_model=PaginatedResponse[BookResponse])
@limiter.limit("100/minute")
def list_books(
    request: Request,
    page: int = Query(1, ge=1, description="Numéro de page"),
    per_page: int = Query(
        settings.PAGINATION_DEFAULT, ge=1, le=settings.PAGINATION_MAX
    ),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    sort_by: str = Query("id", description="Champ de tri (id, title, price, rating)"),
    order: str = Query("asc", description="Ordre de tri (asc, desc)"),
    service: BookService = Depends(get_book_service),
):
    """Récupère une liste paginée de livres avec filtrage et tri.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        page (int): Numéro de page (commence à 1)
        per_page (int): Nombre de livres par page (max: PAGINATION_MAX)
        category (Optional[str]): Filtre par catégorie si fourni
        sort_by (str): Champ de tri (id, title, price, rating)
        order (str): Ordre de tri (asc, desc)
        service (BookService): Service injecté automatiquement

    Returns:
        PaginatedResponse[BookResponse]: Résultats paginés avec métadonnées

    Raises:
        HTTPException: 422 si les paramètres de validation échouent

    Example:
        GET /books?page=1&per_page=20&category=Fiction&sort_by=price&order=desc
    """
    # Validation: sort_by valide
    valid_sort_fields = ["id", "title", "price", "rating"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=422,
            detail=f"sort_by doit être l'un de : {', '.join(valid_sort_fields)}"
        )

    # Validation: order valide
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=422,
            detail="order doit être 'asc' ou 'desc'"
        )

    offset = (page - 1) * per_page
    books = service.repo.get_all(offset=offset, limit=per_page, category=category)
    total = service.get_total_books(category=category)
    total_pages = (total + per_page - 1) // per_page

    # Appliquer le tri si nécessaire
    if category or sort_by != "id" or order != "asc":
        # Utiliser search pour le tri et filtrage
        return service.search_books(
            category=category,
            sort_by=sort_by,
            order=order,
            page=page,
            per_page=per_page,
        )

    return PaginatedResponse[BookResponse](
        items=[BookResponse.model_validate(book) for book in books],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{book_id}", response_model=BookResponse)
@limiter.limit("100/minute")
def get_book(request: Request, book_id: int, service: BookService = Depends(get_book_service)):
    """Récupère les détails d'un livre spécifique par son ID.

    Args:
        request (Request): Requête HTTP (pour rate limiting)
        book_id (int): Identifiant unique du livre
        service (BookService): Service injecté automatiquement

    Returns:
        BookResponse: Détails complets du livre

    Raises:
        HTTPException: 404 si le livre n'existe pas

    Example:
        GET /books/42
    """
    book = service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book