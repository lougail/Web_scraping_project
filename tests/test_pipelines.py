def test_price_normalization():
    """Test de la normalisation des prix dans le pipeline."""
    from books_scraper.books_scraper.pipelines import DataCleaningPipeline
    from itemadapter import ItemAdapter

    pipeline = DataCleaningPipeline()

    # Mock spider pour le logging
    class MockSpider:
        class Logger:
            def warning(self, msg):
                pass
        logger = Logger()

    spider = MockSpider()

    # Test avec prix valide
    item1 = {"price": "£13.50"}
    result1 = pipeline.process_item(item1, spider)
    assert ItemAdapter(result1).get("price") == 13.50

    # Test avec prix à 0
    item2 = {"price": "£0.00"}
    result2 = pipeline.process_item(item2, spider)
    assert ItemAdapter(result2).get("price") == 0.0