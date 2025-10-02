from sqlalchemy import Column, Integer, String, Float, Text
from app.database.session import Base

class Book(Base):
    """Modèle SQLAlchemy pour la table books"""
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
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', price={self.price})>"