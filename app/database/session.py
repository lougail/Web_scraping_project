"""Module de gestion des sessions de base de données avec SQLAlchemy.

Ce module configure le moteur SQLAlchemy, la session factory et la classe de base pour les modèles ORM. Il fournit également la dépendance FastAPI pour l'injection de session de base de données.

Attributes:
    engine (Engine): Moteur SQLAlchemy configuré pour SQLite
    SessionLocal (sessionmaker): Factory pour créer des sessions DB
    Base (DeclarativeMeta): Classe de base pour les modèles ORM

Example:
    >>> from app.database.session import get_db
    >>> def my_endpoint(db: Session = Depends(get_db)):
    ...     books = db.query(Book).all()
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Engine SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """Générateur de session de base de données pour l'injection de dépendances FastAPI.

    Cette fonction est utilisée comme dépendance dans les endpoints FastAPI pour obtenir une session de base de données qui sera automatiquement fermée après le traitement de la requête.

    Yields:
        Session: Session SQLAlchemy active

    Example:
        >>> @app.get("/books")
        >>> def list_books(db: Session = Depends(get_db)):
        ...     return db.query(Book).all()

    Note:
        La session est toujours fermée dans le bloc finally, même en cas d'erreur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()