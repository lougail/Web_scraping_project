"""Repository pour l'accès aux données des livres.

Ce module implémente le pattern Repository pour abstraire l'accès aux données et isoler la logique de requêtage SQL de la logique métier.
"""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, or_, desc, asc
from sqlalchemy.orm import Session
from app.database.models import Book, BookHistory


class BookRepository:
    """Repository pour gérer l'accès aux données des livres.

    Cette classe encapsule toutes les opérations de base de données relatives aux livres, suivant le pattern Repository de la Clean Architecture.

    Attributes:
        db (Session): Session SQLAlchemy pour les opérations de base de données

    Example:
        >>> repo = BookRepository(db_session)
        >>> books = repo.get_all(limit=10)
    """

    def __init__(self, db: Session):
        """Initialise le repository avec une session de base de données.

        Args:
            db (Session): Session SQLAlchemy active
        """
        self.db = db

    def get_all(
        self, offset: int = 0, limit: int = 20, category: Optional[str] = None
    ) -> List[Book]:
        """Récupère une liste paginée de livres avec filtrage optionnel.

        Args:
            offset (int): Nombre de livres à sauter (pour la pagination)
            limit (int): Nombre maximum de livres à retourner
            category (Optional[str]): Filtre par catégorie si fourni

        Returns:
            List[Book]: Liste des livres correspondant aux critères

        Example:
            >>> books = repo.get_all(offset=20, limit=10, category="Fiction")
        """
        query = self.db.query(Book)

        if category:
            query = query.filter(Book.category == category)

        return query.offset(offset).limit(limit).all()

    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Récupère un livre par son identifiant unique.

        Args:
            book_id (int): Identifiant du livre

        Returns:
            Optional[Book]: Le livre trouvé ou None si inexistant

        Example:
            >>> book = repo.get_by_id(42)
        """
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_by_upc(self, upc: str) -> Optional[Book]:
        """Récupère un livre par son code UPC.

        Args:
            upc (str): Universal Product Code du livre

        Returns:
            Optional[Book]: Le livre trouvé ou None si inexistant

        Example:
            >>> book = repo.get_by_upc("a897fe39b1053632")
        """
        return self.db.query(Book).filter(Book.upc == upc).first()

    def count_total(self, category: Optional[str] = None) -> int:
        """Compte le nombre total de livres en base de données.

        Args:
            category (Optional[str]): Filtre par catégorie si fourni

        Returns:
            int: Nombre total de livres (filtré ou non)

        Example:
            >>> total = repo.count_total()
            >>> print(f"Total books: {total}")
            >>> fiction_count = repo.count_total(category="Fiction")
            >>> print(f"Fiction books: {fiction_count}")
        """
        query = self.db.query(Book)
        if category:
            query = query.filter(Book.category == category)
        return query.count()

    def get_average_price(self) -> float:
        """Calcule le prix moyen de tous les livres.

        Returns:
            float: Prix moyen arrondi à 2 décimales, 0.0 si aucun livre

        Example:
            >>> avg = repo.get_average_price()
            >>> print(f"Average price: £{avg}")
        """
        result = self.db.query(func.avg(Book.price)).scalar()
        return round(result, 2) if result else 0.0

    def get_top_categories(self, limit: int = 10) -> List[dict]:
        """Récupère les catégories avec le plus de livres.

        Args:
            limit (int): Nombre maximum de catégories à retourner

        Returns:
            List[dict]: Liste de dictionnaires avec 'category' et 'count'

        Example:
            >>> top = repo.get_top_categories(limit=5)
            >>> for item in top:
            ...     print(f"{item['category']}: {item['count']} books")
        """
        results = (
            self.db.query(Book.category, func.count(Book.id).label("count"))
            .group_by(Book.category)
            .order_by(func.count(Book.id).desc())
            .limit(limit)
            .all()
        )

        return [{"category": r[0], "count": r[1]} for r in results]

    def get_price_by_category(self) -> List[dict]:
        """Calcule le prix moyen des livres par catégorie.

        Returns:
            List[dict]: Liste de dictionnaires avec 'category' et 'avg_price', triée par prix décroissant

        Example:
            >>> prices = repo.get_price_by_category()
            >>> for item in prices:
            ...     print(f"{item['category']}: £{item['avg_price']}")
        """
        results = (
            self.db.query(Book.category, func.avg(Book.price).label("avg_price"))
            .group_by(Book.category)
            .order_by(func.avg(Book.price).desc())
            .all()
        )

        return [{"category": r[0], "avg_price": round(r[1], 2)} for r in results]

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
        offset: int = 0,
        limit: int = 20,
    ) -> List[Book]:
        """Recherche de livres avec filtres multi-critères.

        Args:
            query (Optional[str]): Recherche textuelle dans le titre
            category (Optional[str]): Filtre par catégorie
            min_price (Optional[float]): Prix minimum
            max_price (Optional[float]): Prix maximum
            min_rating (Optional[int]): Note minimum (1-5)
            max_rating (Optional[int]): Note maximum (1-5)
            sort_by (str): Champ de tri (id, title, price, rating)
            order (str): Ordre de tri (asc, desc)
            offset (int): Nombre de livres à sauter
            limit (int): Nombre maximum de livres à retourner

        Returns:
            List[Book]: Liste des livres correspondant aux critères

        Example:
            >>> books = repo.search_books(
            ...     query="python",
            ...     min_price=10.0,
            ...     max_price=50.0,
            ...     sort_by="price",
            ...     order="asc"
            ... )
        """
        q = self.db.query(Book)

        # Recherche textuelle dans le titre
        if query:
            q = q.filter(Book.title.ilike(f"%{query}%"))

        # Filtres
        if category:
            q = q.filter(Book.category == category)
        if min_price is not None:
            q = q.filter(Book.price >= min_price)
        if max_price is not None:
            q = q.filter(Book.price <= max_price)
        if min_rating is not None:
            q = q.filter(Book.rating >= min_rating)
        if max_rating is not None:
            q = q.filter(Book.rating <= max_rating)

        # Tri
        sort_column = getattr(Book, sort_by, Book.id)
        if order == "desc":
            q = q.order_by(desc(sort_column))
        else:
            q = q.order_by(asc(sort_column))

        return q.offset(offset).limit(limit).all()

    def count_search_results(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
    ) -> int:
        """Compte le nombre de résultats d'une recherche.

        Args:
            query (Optional[str]): Recherche textuelle dans le titre
            category (Optional[str]): Filtre par catégorie
            min_price (Optional[float]): Prix minimum
            max_price (Optional[float]): Prix maximum
            min_rating (Optional[int]): Note minimum
            max_rating (Optional[int]): Note maximum

        Returns:
            int: Nombre de livres correspondant aux critères

        Example:
            >>> count = repo.count_search_results(query="python", min_price=10.0)
        """
        q = self.db.query(Book)

        if query:
            q = q.filter(Book.title.ilike(f"%{query}%"))
        if category:
            q = q.filter(Book.category == category)
        if min_price is not None:
            q = q.filter(Book.price >= min_price)
        if max_price is not None:
            q = q.filter(Book.price <= max_price)
        if min_rating is not None:
            q = q.filter(Book.rating >= min_rating)
        if max_rating is not None:
            q = q.filter(Book.rating <= max_rating)

        return q.count()

    def get_all_categories(self) -> List[str]:
        """Récupère la liste de toutes les catégories uniques.

        Returns:
            List[str]: Liste des catégories triées alphabétiquement

        Example:
            >>> categories = repo.get_all_categories()
            >>> print(categories)
            ['Fiction', 'Mystery', 'Science', ...]
        """
        results = (
            self.db.query(Book.category)
            .filter(Book.category.isnot(None))
            .distinct()
            .order_by(Book.category)
            .all()
        )

        return [r[0] for r in results]

    def get_random_books(self, limit: int = 10) -> List[Book]:
        """Récupère des livres aléatoires.

        Args:
            limit (int): Nombre de livres à retourner

        Returns:
            List[Book]: Liste de livres aléatoires

        Example:
            >>> random_books = repo.get_random_books(limit=5)
        """
        return self.db.query(Book).order_by(func.random()).limit(limit).all()

    def get_rating_distribution(self) -> List[dict]:
        """Calcule la distribution des notes (1-5 étoiles).

        Returns:
            List[dict]: Liste de dictionnaires avec 'rating' et 'count'

        Example:
            >>> dist = repo.get_rating_distribution()
            >>> for item in dist:
            ...     print(f"{item['rating']} étoiles: {item['count']} livres")
        """
        results = (
            self.db.query(Book.rating, func.count(Book.id).label("count"))
            .filter(Book.rating.isnot(None))
            .group_by(Book.rating)
            .order_by(Book.rating)
            .all()
        )

        return [{"rating": r[0], "count": r[1]} for r in results]

    def get_price_ranges(self) -> List[dict]:
        """Calcule la distribution des prix par tranches.

        Returns:
            List[dict]: Liste de dictionnaires avec 'range' et 'count'

        Example:
            >>> ranges = repo.get_price_ranges()
            >>> for item in ranges:
            ...     print(f"{item['range']}: {item['count']} livres")
        """
        # Définir les tranches de prix
        ranges = [
            ("0-10", 0, 10),
            ("10-20", 10, 20),
            ("20-30", 20, 30),
            ("30-40", 30, 40),
            ("40-50", 40, 50),
            ("50+", 50, float('inf'))
        ]

        results = []
        for range_name, min_p, max_p in ranges:
            if max_p == float('inf'):
                count = self.db.query(Book).filter(Book.price >= min_p).count()
            else:
                count = self.db.query(Book).filter(
                    Book.price >= min_p, Book.price < max_p
                ).count()
            results.append({"range": range_name, "count": count})

        return results

    # ===== MÉTHODES POUR L'HISTORIQUE =====

    def get_book_history(
        self,
        book_id: int,
        days: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[BookHistory]:
        """Récupère l'historique complet d'un livre.

        Args:
            book_id (int): Identifiant du livre
            days (Optional[int]): Limiter aux N derniers jours
            limit (Optional[int]): Nombre maximum d'entrées à retourner

        Returns:
            List[BookHistory]: Liste des entrées historiques triées par date décroissante

        Example:
            >>> history = repo.get_book_history(book_id=1, days=30)
        """
        query = self.db.query(BookHistory).filter(BookHistory.book_id == book_id)

        if days:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(BookHistory.scraped_at >= cutoff_date)

        query = query.order_by(desc(BookHistory.scraped_at))

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_price_history(self, book_id: int, days: Optional[int] = None) -> List[dict]:
        """Récupère l'historique des prix d'un livre.

        Args:
            book_id (int): Identifiant du livre
            days (Optional[int]): Limiter aux N derniers jours

        Returns:
            List[dict]: Liste avec 'date' et 'price'

        Example:
            >>> prices = repo.get_price_history(book_id=1, days=7)
            >>> for entry in prices:
            ...     print(f"{entry['date']}: £{entry['price']}")
        """
        query = self.db.query(
            BookHistory.scraped_at,
            BookHistory.price
        ).filter(BookHistory.book_id == book_id)

        if days:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(BookHistory.scraped_at >= cutoff_date)

        query = query.order_by(BookHistory.scraped_at)

        results = query.all()
        return [{"date": r[0], "price": r[1]} for r in results]

    def get_recent_price_changes(self, days: int = 7, limit: int = 50) -> List[dict]:
        """Récupère les livres dont le prix a changé récemment.

        Args:
            days (int): Nombre de jours à analyser
            limit (int): Nombre maximum de résultats

        Returns:
            List[dict]: Liste des changements avec book_id, title, old_price, new_price, etc.

        Example:
            >>> changes = repo.get_recent_price_changes(days=7)
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Sous-requête pour obtenir les 2 dernières entrées de chaque livre
        subquery = (
            self.db.query(
                BookHistory.book_id,
                BookHistory.price,
                BookHistory.scraped_at,
                func.row_number().over(
                    partition_by=BookHistory.book_id,
                    order_by=desc(BookHistory.scraped_at)
                ).label('rn')
            )
            .filter(BookHistory.scraped_at >= cutoff_date)
            .subquery()
        )

        # Récupérer les livres avec changement de prix
        results = []
        books_with_changes = (
            self.db.query(subquery.c.book_id)
            .filter(subquery.c.rn <= 2)
            .group_by(subquery.c.book_id)
            .having(func.count(subquery.c.book_id) == 2)
            .all()
        )

        for (book_id,) in books_with_changes[:limit]:
            # Récupérer les 2 dernières entrées
            history_entries = (
                self.db.query(BookHistory)
                .filter(BookHistory.book_id == book_id)
                .filter(BookHistory.scraped_at >= cutoff_date)
                .order_by(desc(BookHistory.scraped_at))
                .limit(2)
                .all()
            )

            if len(history_entries) == 2:
                new_entry = history_entries[0]
                old_entry = history_entries[1]

                if new_entry.price != old_entry.price:
                    book = self.db.query(Book).filter(Book.id == book_id).first()
                    if book:
                        change_percent = ((new_entry.price - old_entry.price) / old_entry.price) * 100

                        results.append({
                            "book_id": book_id,
                            "upc": book.upc,
                            "title": book.title,
                            "old_price": old_entry.price,
                            "new_price": new_entry.price,
                            "change_percent": round(change_percent, 2),
                            "changed_at": new_entry.scraped_at
                        })

        return results

    def get_stock_alerts(self, threshold: int = 10) -> List[dict]:
        """Récupère les livres avec un stock faible ou en rupture.

        Args:
            threshold (int): Seuil de stock faible

        Returns:
            List[dict]: Liste des livres avec stock faible

        Example:
            >>> alerts = repo.get_stock_alerts(threshold=5)
        """
        results = []
        books = self.db.query(Book).filter(Book.stock <= threshold).all()

        for book in books:
            # Récupérer la dernière entrée historique
            last_history = (
                self.db.query(BookHistory)
                .filter(BookHistory.book_id == book.id)
                .order_by(desc(BookHistory.scraped_at))
                .first()
            )

            results.append({
                "book_id": book.id,
                "upc": book.upc,
                "title": book.title,
                "current_stock": book.stock,
                "last_checked": last_history.scraped_at if last_history else None,
                "status": "out_of_stock" if book.stock == 0 else "low_stock"
            })

        return results