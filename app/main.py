from fastapi import FastAPI
from app.config import settings
from app.routers import books, stats

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API de veille concurrentielle pour books.toscrape.com"
)

# Inclure les routers
app.include_router(books.router)
app.include_router(stats.router)

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