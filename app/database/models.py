from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Book(Base):
    """Modèle SQLAlchemy pour la table books

    Attributes:
        id (int): Identifiant unique du livre
        upc (str): Universal Product Code
        title (str): Titre du livre
        price (float): Prix en livres sterling
        rating (int): Note de 1 à 5 étoiles
        stock (int): Nombre d'exemplaires en stock
        category (str): Catégorie du livre
        description (str): Description détaillée
        number_of_reviews (int): Nombre de critiques
        cover (str): URL de l'image de couverture
        product_type (str): Type de produit
        scraped_at (datetime): Date et heure du scraping initial
        last_updated (datetime): Date et heure de la dernière mise à jour
        history (relationship): Relation vers l'historique des modifications
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    upc = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Integer)
    stock = Column(Integer)
    category = Column(String(100), index=True)
    description = Column(Text)
    number_of_reviews = Column(Integer)
    cover = Column(String(500))
    product_type = Column(String(50))
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relation vers l'historique
    history = relationship("BookHistory", back_populates="book", cascade="all, delete-orphan")

    # Index composites pour améliorer les performances des requêtes de filtrage
    __table_args__ = (
        Index('idx_category_price', 'category', 'price'),
        Index('idx_category_rating', 'category', 'rating'),
        Index('idx_price_rating', 'price', 'rating'),
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', price={self.price})>"


class BookHistory(Base):
    """Modèle SQLAlchemy pour l'historique des modifications de livres

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

    id = Column(Integer, primary_key=True, index=True)
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

    # Index composites pour requêtes d'analyse
    __table_args__ = (
        Index('idx_book_date', 'book_id', 'scraped_at'),
        Index('idx_upc_date', 'upc', 'scraped_at'),
    )

    def __repr__(self):
        return f"<BookHistory(book_id={self.book_id}, price={self.price}, scraped_at={self.scraped_at})>"
