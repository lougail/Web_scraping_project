from sqlalchemy import Column, Integer, String, Float, Text
from books_scraper.database.connection import Base

class Book(Base):
    """Model for the book table

    Args:
        Base (Base): The base of the database

    Returns:
        Book: The book model
    """
    __tablename__ = "books"
    
    # Primary key  (auto-increment)
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Fields
    upc = Column(String(20), unique=True, nullable=False)  # Unique and not null
    title = Column(String(255), nullable=False)
    price = Column(Float)
    rating = Column(Integer)
    stock = Column(Integer)
    category = Column(String(100))
    description = Column(Text)
    number_of_reviews = Column(Integer)
    cover = Column(String(500))
    product_type = Column(String(50))
    
    def __repr__(self):
        """Représentation lisible de l'objet"""
        return f"<Book(title='{self.title}', price={self.price})>"