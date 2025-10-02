from app.schemas.book import BookResponse
import pytest
from pydantic import ValidationError

def test_book_response_valid():
    book = BookResponse(
        id=1,
        title="Test Book",
        price=10.99,
        category="Fiction",
        rating=4,
        stock=3,
        upc="1234567890",
        description="Une description.",
        cover="http://example.com/image.jpg",
        product_type="Book",
        number_of_reviews=2
    )
    assert book.title == "Test Book"
    assert book.price > 0
    assert book.upc == "1234567890"

def test_book_response_invalid_price():
    with pytest.raises(ValidationError):
        BookResponse(
            id=2,
            title="Oups",
            price=-5.0,  # Prix négatif --> doit échouer si tu as une validation, sinon adapte ou retire ce test
            category="Fiction",
            rating=3,
            stock=2,
            upc="0987654321",
            description="Bad price"
        )

def test_book_response_invalid_rating():
    with pytest.raises(ValidationError):
        BookResponse(
            id=3,
            title="Bad rating",
            price=12.2,
            category="Fiction",
            rating=7,  # Si tu ajoutes une validation stricte sur rating [1-5]
            stock=1,
            upc="5555555555",
            description="Invalid rating"
        )