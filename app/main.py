from fastapi import FastAPI
from app.config import settings
from app.routers.books import router as books_router
from app.routers.stats import router as stats_router
from app.error_handlers import register_error_handlers

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API de veille concurrentielle pour books.toscrape.com"
)

register_error_handlers(app)

# Inclure les routers
app.include_router(books_router)
app.include_router(stats_router)

@app.get("/")
def root():
    return {
        "message": "Books Competitive Intelligence API",
        "version": settings.VERSION,
        "documentation": "/docs",
        "endpoints": {
            "books": "/books",
            "book_detail": "/books/{id}",
            "statistics": "/stats"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}