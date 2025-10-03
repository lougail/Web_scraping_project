"""Modèles SQLAlchemy pour le projet Scrapy.

Ce module définit les modèles ORM représentant les tables de la base de données utilisée par le scraper pour stocker les données de livres et leur historique.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from books_scraper.books_scraper.database.connection import Base


class Book(Base):
    """Modèle SQLAlchemy représentant un livre dans la base de données.

    Cette classe définit la structure de la table 'books' utilisée par le scraper pour stocker les données extraites de books.toscrape.com.

    Attributes:
        id (int): Identifiant unique auto-incrémenté (clé primaire)
        upc (str): Universal Product Code, identifiant unique du produit (unique, non null)
        title (str): Titre du livre (non null)
        price (float): Prix du livre en livres sterling
        rating (int): Note du livre de 1 à 5 étoiles
        stock (int): Nombre d'exemplaires disponibles en stock
        category (str): Catégorie du livre (Fiction, Mystery, etc.)
        description (str): Description longue du livre
        number_of_reviews (int): Nombre de critiques/reviews du livre
        cover (str): URL complète de la couverture du livre
        product_type (str): Type de produit (généralement "Books")
        history (relationship): Relation vers l'historique des modifications

    Example:
        >>> book = Book(
        ...     upc="abc123",
        ...     title="Clean Code",
        ...     price=29.99,
        ...     rating=5
        ... )
        >>> session.add(book)
        >>> session.commit()

    Note:
        Le champ UPC est unique et indexé pour éviter les doublons et accélérer les requêtes.
    """

    __tablename__ = "books"

    # Clé primaire auto-incrémentée
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Champs du livre
    upc = Column(String(20), unique=True, nullable=False)  # Unique et non null
    title = Column(String(255), nullable=False)
    price = Column(Float)
    rating = Column(Integer)
    stock = Column(Integer)
    category = Column(String(100))
    description = Column(Text)
    number_of_reviews = Column(Integer)
    cover = Column(String(500))
    product_type = Column(String(50))

    # Relation vers l'historique
    history = relationship("BookHistory", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        """Représentation lisible de l'objet Book.

        Returns:
            str: Chaîne de caractères représentant le livre avec titre et prix
        """
        return f"<Book(title='{self.title}', price={self.price})>"


class BookHistory(Base):
    """Modèle SQLAlchemy pour l'historique des modifications de livres.

    Ce modèle permet de tracker l'évolution de certains champs clés au fil du temps, notamment pour la veille concurrentielle (prix, stock, popularité).

    Attributes:
        id (int): Identifiant unique de l'entrée historique
        book_id (int): Référence vers le livre (clé étrangère)
        upc (str): Universal Product Code (dénormalisé pour performance)
        price (float): Prix au moment du snapshot
        stock (int): Stock disponible au moment du snapshot
        rating (int): Note (1-5 étoiles) au moment du snapshot
        number_of_reviews (int): Nombre de critiques au moment du snapshot
        scraped_at (datetime): Date et heure du snapshot
        book (relationship): Relation vers le livre parent

    Example:
        >>> # Récupérer l'historique des prix d'un livre
        >>> history = session.query(BookHistory).filter_by(book_id=1).order_by(BookHistory.scraped_at).all()
        >>> for entry in history:
        ...     print(f"{entry.scraped_at}: £{entry.price}")
    """
    __tablename__ = "book_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'), nullable=False, index=True)
    upc = Column(String(20), nullable=False, index=True)

    # Champs trackés (snapshot à chaque scraping si changement détecté)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    rating = Column(Integer)
    number_of_reviews = Column(Integer)

    # Métadonnées
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relation vers le livre parent
    book = relationship("Book", back_populates="history")

    def __repr__(self):
        return f"<BookHistory(book_id={self.book_id}, price={self.price}, scraped_at={self.scraped_at})>"
