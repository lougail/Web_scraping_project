def test_scrapy_item_fields():
    from books_scraper.books_scraper.items import BookItem
    item = BookItem(title="Test", price=10.0, category="Fiction")
    assert "title" in item
    assert "price" in item
    assert "category" in item