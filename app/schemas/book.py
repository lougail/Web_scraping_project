"""Schémas Pydantic pour la validation et sérialisation des données.

Ce module définit les modèles Pydantic utilisés pour valider les requêtes et formater les réponses de l'API. Ils assurent la cohérence des données et génèrent automatiquement la documentation OpenAPI.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class BookBase(BaseModel):
    """Schéma de base pour un livre.

    Contient les champs communs partagés entre différents schémas de livre.
    Utilisé comme classe de base pour les autres schémas.

    Attributes:
        title (str): Titre du livre
        price (float): Prix du livre en livres sterling
        rating (Optional[int]): Note du livre de 1 à 5 étoiles
        stock (Optional[int]): Nombre d'exemplaires en stock
        category (Optional[str]): Catégorie du livre
    """

    title: str = Field(..., description="Titre du livre", min_length=1, max_length=255)
    price: float = Field(..., description="Prix en livres sterling", gt=0)
    rating: Optional[int] = Field(None, description="Note de 1 à 5 étoiles", ge=1, le=5)
    stock: Optional[int] = Field(None, description="Nombre d'exemplaires disponibles", ge=0)
    category: Optional[str] = Field(None, description="Catégorie du livre", max_length=100)


class BookResponse(BookBase):
    """Schéma de réponse pour un livre complet.

    Hérite de BookBase et ajoute tous les champs supplémentaires retournés par l'API lors de la consultation d'un livre.

    Attributes:
        id (int): Identifiant unique du livre
        upc (str): Universal Product Code
        description (Optional[str]): Description détaillée du livre
        cover (Optional[str]): URL de l'image de couverture
        product_type (Optional[str]): Type de produit
        number_of_reviews (Optional[int]): Nombre de critiques

    Example:
        >>> book = BookResponse(
        ...     id=1,
        ...     upc="abc123",
        ...     title="Clean Code",
        ...     price=29.99
        ... )
    """

    id: int
    upc: str
    description: Optional[str] = None
    cover: Optional[str] = None
    product_type: Optional[str] = None
    number_of_reviews: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryStats(BaseModel):
    """Schéma pour les statistiques par catégorie.

    Utilisé pour retourner le nombre de livres par catégorie.

    Attributes:
        category (str): Nom de la catégorie
        count (int): Nombre de livres dans cette catégorie

    Example:
        >>> stats = CategoryStats(category="Fiction", count=42)
    """

    category: str = Field(..., description="Nom de la catégorie")
    count: int = Field(..., description="Nombre de livres", ge=0)


class PriceStats(BaseModel):
    """Schéma pour les statistiques de prix par catégorie.

    Utilisé pour retourner le prix moyen des livres par catégorie.

    Attributes:
        category (str): Nom de la catégorie
        avg_price (float): Prix moyen des livres dans cette catégorie

    Example:
        >>> stats = PriceStats(category="Fiction", avg_price=24.99)
    """

    category: str = Field(..., description="Nom de la catégorie")
    avg_price: float = Field(..., description="Prix moyen en livres sterling", ge=0)


class GeneralStats(BaseModel):
    """Schéma pour les statistiques générales sur tous les livres.

    Utilisé pour retourner des métriques globales de la bibliothèque.

    Attributes:
        total_books (int): Nombre total de livres
        average_price (float): Prix moyen de tous les livres

    Example:
        >>> stats = GeneralStats(total_books=1000, average_price=35.50)
    """

    total_books: int = Field(..., description="Nombre total de livres", ge=0)
    average_price: float = Field(..., description="Prix moyen en livres sterling", ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    """Schéma générique pour les réponses paginées.

    Permet de retourner une liste d'items avec des métadonnées de pagination.

    Attributes:
        items (List[T]): Liste des éléments de la page actuelle
        total (int): Nombre total d'éléments dans la base
        page (int): Numéro de la page actuelle
        per_page (int): Nombre d'éléments par page
        total_pages (int): Nombre total de pages

    Example:
        >>> response = PaginatedResponse[BookResponse](
        ...     items=[book1, book2],
        ...     total=100,
        ...     page=1,
        ...     per_page=20,
        ...     total_pages=5
        ... )
    """

    items: List[T]
    total: int = Field(..., description="Nombre total d'éléments", ge=0)
    page: int = Field(..., description="Numéro de la page actuelle", ge=1)
    per_page: int = Field(..., description="Nombre d'éléments par page", ge=1)
    total_pages: int = Field(..., description="Nombre total de pages", ge=0)


class RatingDistribution(BaseModel):
    """Schéma pour la distribution des notes.

    Attributes:
        rating (int): Valeur de la note (1-5)
        count (int): Nombre de livres avec cette note

    Example:
        >>> dist = RatingDistribution(rating=5, count=120)
    """

    rating: int = Field(..., description="Note (1-5 étoiles)", ge=1, le=5)
    count: int = Field(..., description="Nombre de livres", ge=0)


class PriceRange(BaseModel):
    """Schéma pour les tranches de prix.

    Attributes:
        range (str): Description de la tranche de prix
        count (int): Nombre de livres dans cette tranche

    Example:
        >>> range_stat = PriceRange(range="0-10", count=45)
    """

    range: str = Field(..., description="Tranche de prix")
    count: int = Field(..., description="Nombre de livres", ge=0)


class BookHistoryEntry(BaseModel):
    """Schéma pour une entrée historique d'un livre.

    Attributes:
        id (int): Identifiant de l'entrée historique
        book_id (int): Identifiant du livre
        upc (str): Universal Product Code
        price (float): Prix au moment du snapshot
        stock (int): Stock disponible
        rating (Optional[int]): Note (1-5 étoiles)
        number_of_reviews (Optional[int]): Nombre de critiques
        scraped_at (datetime): Date et heure du snapshot

    Example:
        >>> entry = BookHistoryEntry(
        ...     id=1,
        ...     book_id=42,
        ...     upc="abc123",
        ...     price=25.99,
        ...     stock=15,
        ...     rating=4,
        ...     number_of_reviews=120,
        ...     scraped_at=datetime.now()
        ... )
    """

    id: int
    book_id: int
    upc: str
    price: float = Field(..., description="Prix en livres sterling", gt=0)
    stock: int = Field(..., description="Stock disponible", ge=0)
    rating: Optional[int] = Field(None, description="Note (1-5 étoiles)", ge=1, le=5)
    number_of_reviews: Optional[int] = Field(None, description="Nombre de critiques", ge=0)
    scraped_at: datetime = Field(..., description="Date et heure du snapshot")

    model_config = ConfigDict(from_attributes=True)


class PriceEvolution(BaseModel):
    """Schéma pour l'évolution du prix d'un livre.

    Attributes:
        date (datetime): Date du snapshot
        price (float): Prix à cette date

    Example:
        >>> evolution = PriceEvolution(date=datetime.now(), price=25.99)
    """

    date: datetime = Field(..., description="Date du snapshot")
    price: float = Field(..., description="Prix en livres sterling", gt=0)


class PriceChange(BaseModel):
    """Schéma pour un changement de prix détecté.

    Attributes:
        book_id (int): Identifiant du livre
        upc (str): Universal Product Code
        title (str): Titre du livre
        old_price (float): Ancien prix
        new_price (float): Nouveau prix
        change_percent (float): Pourcentage de changement
        changed_at (datetime): Date du changement

    Example:
        >>> change = PriceChange(
        ...     book_id=1,
        ...     upc="abc123",
        ...     title="Clean Code",
        ...     old_price=30.0,
        ...     new_price=25.0,
        ...     change_percent=-16.67,
        ...     changed_at=datetime.now()
        ... )
    """

    book_id: int
    upc: str
    title: str
    old_price: float = Field(..., description="Ancien prix", gt=0)
    new_price: float = Field(..., description="Nouveau prix", gt=0)
    change_percent: float = Field(..., description="Pourcentage de changement")
    changed_at: datetime = Field(..., description="Date du changement")
