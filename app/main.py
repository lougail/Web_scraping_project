"""Application FastAPI principale pour l'API de veille concurrentielle de livres.

Ce module initialise l'application FastAPI, configure les routers et expose les endpoints de base (root et health check).

Typical usage example:
    uvicorn app.main:app --reload
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers.books import router as books_router
from app.routers.stats import router as stats_router
from app.routers.history import router as history_router
from app.error_handlers import register_error_handlers

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter (in-memory storage)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    storage_uri="memory://"
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API de veille concurrentielle pour books.toscrape.com"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS pour les frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production: spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression des réponses
app.add_middleware(GZipMiddleware, minimum_size=1000)

register_error_handlers(app)

# Inclure les routers
app.include_router(books_router)
app.include_router(stats_router)
app.include_router(history_router)

logger.info(f"Application {settings.APP_NAME} v{settings.VERSION} démarrée")


@app.get("/")
def root():
    """Endpoint racine de l'API.

    Fournit des informations sur l'API et liste les endpoints disponibles.

    Returns:
        dict: Un dictionnaire contenant :
            - message (str): Nom de l'API
            - version (str): Version de l'API
            - documentation (str): URL de la documentation Swagger
            - endpoints (dict): Liste des principaux endpoints disponibles

    Example:
        >>> GET /
        {
            "message": "Books Competitive Intelligence API",
            "version": "1.0.0",
            "documentation": "/docs",
            "endpoints": {...}
        }
    """
    return {
        "message": "Books Competitive Intelligence API",
        "version": settings.VERSION,
        "documentation": "/docs",
        "endpoints": {
            "books": "/books",
            "book_detail": "/books/{id}",
            "books_count": "/books/count",
            "statistics": "/stats",
            "history": "/history"
        }
    }


@app.get("/health")
def health():
    """Endpoint de health check pour vérifier l'état de l'API et de la DB.

    Utilisé par les systèmes de monitoring et les orchestrateurs (Docker, K8s) pour vérifier que l'application fonctionne correctement.

    Returns:
        dict: Un dictionnaire avec le statut de l'application et de la DB.
            - status (str): "healthy" si l'application fonctionne
            - database (str): "connected" si la DB est accessible

    Example:
        >>> GET /health
        {"status": "healthy", "database": "connected"}
    """
    from app.database.session import SessionLocal
    from sqlalchemy import text

    db_status = "disconnected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"

    return {"status": "healthy", "database": db_status}