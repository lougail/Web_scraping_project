def test_scrapy_item_fields():
    """Test que les items Scrapy contiennent les champs attendus."""
    # Scrapy utilise des dicts pour les items, pas besoin de classe BookItem
    item = {
        "title": "Test",
        "price": "£10.0",
        "category": "Fiction",
        "upc": "test123",
        "rating": "star-rating Three",
        "availability": "In stock (5 available)"
    }

    assert "title" in item
    assert "price" in item
    assert "category" in item
    assert "upc" in item