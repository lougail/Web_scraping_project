def test_price_normalization():
    from books_scraper.books_scraper.pipelines import normalize_price
    assert normalize_price("£13.50") == 13.50
    assert normalize_price("£0.00") == 0.0