"""Service contenant la logique métier pour les livres.

Ce module implémente la couche service (use cases) de la Clean Architecture, orchestrant les appels au repository et appliquant les règles métier.
"""

from typing import List, Optional
from math import ceil
from sqlalchemy.orm import Session
from app.repositories.book_repository import BookRepository
from app.schemas.book import (
    BookResponse,
    CategoryStats,
    PriceStats,
    PaginatedResponse,
    RatingDistribution,
    PriceRange,
    BookHistoryEntry,
    PriceEvolution,
    PriceChange
)


class BookService:
    """Service orchestrant la logique métier pour les livres.

    Cette classe fait le pont entre les routers (API) et le repository (DB), en appliquant les transformations de données et les règles métier nécessaires.

    Attributes:
        repo (BookRepository): Repository pour l'accès aux données

    Example:
        >>> service = BookService(db_session)
        >>> books = service.list_books(page=1, per_page=10)
    """

    def __init__(self, db: Session):
        """Initialise le service avec une session de base de données.

        Args:
            db (Session): Session SQLAlchemy active
        """
        self.repo = BookRepository(db)

    def list_books(
        self, page: int = 1, per_page: int = 20, category: Optional[str] = None
    ) -> List[BookResponse]:
        """Récupère une liste paginée de livres avec filtrage optionnel.

        Transforme les objets ORM en schémas Pydantic pour l'API.

        Args:
            page (int): Numéro de page (commence à 1)
            per_page (int): Nombre de livres par page
            category (Optional[str]): Filtre par catégorie si fourni

        Returns:
            List[BookResponse]: Liste de livres formatés pour la réponse API

        Example:
            >>> books = service.list_books(page=2, per_page=20, category="Fiction")
        """
        offset = (page - 1) * per_page
        books = self.repo.get_all(offset=offset, limit=per_page, category=category)
        return [BookResponse.model_validate(book) for book in books]

    def get_book(self, book_id: int) -> Optional[BookResponse]:
        """Récupère un livre par son identifiant.

        Args:
            book_id (int): Identifiant unique du livre

        Returns:
            Optional[BookResponse]: Le livre trouvé ou None si inexistant

        Example:
            >>> book = service.get_book(42)
            >>> if book:
            ...     print(book.title)
        """
        book = self.repo.get_by_id(book_id)
        return BookResponse.model_validate(book) if book else None

    def get_total_books(self, category: Optional[str] = None) -> int:
        """Compte le nombre total de livres en base de données.

        Args:
            category (Optional[str]): Filtre par catégorie si fourni

        Returns:
            int: Nombre total de livres (filtré ou non)

        Example:
            >>> total = service.get_total_books()
            >>> fiction_total = service.get_total_books(category="Fiction")
        """
        return self.repo.count_total(category=category)

    def get_average_price(self) -> float:
        """Calcule le prix moyen de tous les livres.

        Returns:
            float: Prix moyen arrondi à 2 décimales

        Example:
            >>> avg = service.get_average_price()
        """
        return self.repo.get_average_price()

    def get_top_categories(self, limit: int = 10) -> List[CategoryStats]:
        """Récupère les catégories avec le plus de livres.

        Args:
            limit (int): Nombre maximum de catégories à retourner

        Returns:
            List[CategoryStats]: Liste des statistiques par catégorie

        Example:
            >>> top = service.get_top_categories(limit=5)
        """
        results = self.repo.get_top_categories(limit)
        return [CategoryStats(**r) for r in results]

    def get_price_by_category(self) -> List[PriceStats]:
        """Calcule le prix moyen des livres par catégorie.

        Returns:
            List[PriceStats]: Liste des prix moyens par catégorie

        Example:
            >>> prices = service.get_price_by_category()
        """
        results = self.repo.get_price_by_category()
        return [PriceStats(**r) for r in results]

    def search_books(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        sort_by: str = "id",
        order: str = "asc",
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResponse[BookResponse]:
        """Recherche de livres avec filtres multi-critères et pagination.

        Args:
            query (Optional[str]): Recherche textuelle dans le titre
            category (Optional[str]): Filtre par catégorie
            min_price (Optional[float]): Prix minimum
            max_price (Optional[float]): Prix maximum
            min_rating (Optional[int]): Note minimum
            max_rating (Optional[int]): Note maximum
            sort_by (str): Champ de tri (id, title, price, rating)
            order (str): Ordre de tri (asc, desc)
            page (int): Numéro de page
            per_page (int): Nombre de livres par page

        Returns:
            PaginatedResponse[BookResponse]: Résultats paginés avec métadonnées

        Example:
            >>> results = service.search_books(
            ...     query="python",
            ...     min_price=10.0,
            ...     sort_by="price",
            ...     page=1,
            ...     per_page=20
            ... )
        """
        offset = (page - 1) * per_page

        books = self.repo.search_books(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            max_rating=max_rating,
            sort_by=sort_by,
            order=order,
            offset=offset,
            limit=per_page,
        )

        total = self.repo.count_search_results(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            max_rating=max_rating,
        )

        total_pages = ceil(total / per_page) if per_page > 0 else 0

        return PaginatedResponse[BookResponse](
            items=[BookResponse.model_validate(book) for book in books],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    def get_categories(self) -> List[str]:
        """Récupère la liste de toutes les catégories uniques.

        Returns:
            List[str]: Liste des catégories triées alphabétiquement

        Example:
            >>> categories = service.get_categories()
        """
        return self.repo.get_all_categories()

    def get_random_books(self, limit: int = 10) -> List[BookResponse]:
        """Récupère des livres aléatoires.

        Args:
            limit (int): Nombre de livres à retourner

        Returns:
            List[BookResponse]: Liste de livres aléatoires

        Example:
            >>> books = service.get_random_books(limit=5)
        """
        books = self.repo.get_random_books(limit)
        return [BookResponse.model_validate(book) for book in books]

    def get_rating_distribution(self) -> List[RatingDistribution]:
        """Calcule la distribution des notes.

        Returns:
            List[RatingDistribution]: Distribution des notes de 1 à 5

        Example:
            >>> dist = service.get_rating_distribution()
        """
        results = self.repo.get_rating_distribution()
        return [RatingDistribution(**r) for r in results]

    def get_price_ranges(self) -> List[PriceRange]:
        """Calcule la distribution des prix par tranches.

        Returns:
            List[PriceRange]: Distribution des prix par tranches

        Example:
            >>> ranges = service.get_price_ranges()
        """
        results = self.repo.get_price_ranges()
        return [PriceRange(**r) for r in results]

    # ===== MÉTHODES POUR L'HISTORIQUE =====

    def get_book_history(
        self,
        book_id: int,
        days: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[BookHistoryEntry]:
        """Récupère l'historique complet d'un livre.

        Args:
            book_id (int): Identifiant du livre
            days (Optional[int]): Limiter aux N derniers jours
            limit (Optional[int]): Nombre maximum d'entrées

        Returns:
            List[BookHistoryEntry]: Historique du livre

        Example:
            >>> history = service.get_book_history(book_id=1, days=30)
        """
        history = self.repo.get_book_history(book_id, days, limit)
        return [BookHistoryEntry.model_validate(h) for h in history]

    def get_price_history(self, book_id: int, days: Optional[int] = None) -> List[PriceEvolution]:
        """Récupère l'évolution des prix d'un livre.

        Args:
            book_id (int): Identifiant du livre
            days (Optional[int]): Limiter aux N derniers jours

        Returns:
            List[PriceEvolution]: Évolution des prix

        Example:
            >>> prices = service.get_price_history(book_id=1, days=7)
        """
        results = self.repo.get_price_history(book_id, days)
        return [PriceEvolution(**r) for r in results]

    def get_recent_price_changes(self, days: int = 7, limit: int = 50) -> List[PriceChange]:
        """Récupère les changements de prix récents.

        Args:
            days (int): Nombre de jours à analyser
            limit (int): Nombre maximum de résultats

        Returns:
            List[PriceChange]: Liste des changements de prix

        Example:
            >>> changes = service.get_recent_price_changes(days=7)
        """
        results = self.repo.get_recent_price_changes(days, limit)
        return [PriceChange(**r) for r in results]

    def get_stock_alerts(self, threshold: int = 10) -> List[dict]:
        """Récupère les alertes de stock faible.

        Args:
            threshold (int): Seuil de stock faible

        Returns:
            List[dict]: Liste des livres en stock faible

        Example:
            >>> alerts = service.get_stock_alerts(threshold=5)
        """
        return self.repo.get_stock_alerts(threshold)