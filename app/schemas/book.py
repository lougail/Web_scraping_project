from pydantic import BaseModel, ConfigDict
from typing import Optional

class BookBase(BaseModel):
    """Schema de base pour un livre"""
    title: str
    price: float
    rating: Optional[int] = None
    stock: Optional[int] = None
    category: Optional[str] = None

class BookResponse(BookBase):
    """Schema de réponse API"""
    id: int
    upc: str
    description: Optional[str] = None
    cover: Optional[str] = None
    product_type: Optional[str] = None
    number_of_reviews: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class CategoryStats(BaseModel):
    """Statistiques par catégorie"""
    category: str
    count: int

class PriceStats(BaseModel):
    """Statistiques de prix par catégorie"""
    category: str
    avg_price: float