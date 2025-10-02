from pathlib import Path
from pydantic_settings import BaseSettings

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
SCRAPY_PROJECT_DIR = BASE_DIR / "books_scraper"
DB_PATH = SCRAPY_PROJECT_DIR / "books.db"

class Settings(BaseSettings):
    """Configuration centralisée de l'application"""
    
    # Application
    APP_NAME: str = "Books Competitive Intelligence API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    
    # Pagination
    PAGINATION_DEFAULT: int = 20
    PAGINATION_MAX: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()