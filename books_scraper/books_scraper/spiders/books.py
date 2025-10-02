import scrapy

class BooksSpider(scrapy.Spider):
    """
    Spider to scrape the books from the website

    Args:
        scrapy (Spider): The spider class

    Yields:
        dict: A dictionary containing the book details
    """
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com"]

    def parse(self, response):
        """
        Parse the main page

        Args:
            response (Response): The response object

        Yields:
            dict: A dictionary containing the book details
        """
        for book in response.css('article.product_pod'):
            book_url = book.css('h3 a::attr(href)').get()
            if book_url:
                yield response.follow(book_url, callback=self.parse_book_detail)
        
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(self, response):
        """
        Parse the book detail page

        Args:
            response (Response): The response object

        Yields:
            dict: A dictionary containing the book details
        """
        yield {
            'title': response.css('h1::text').get(),
            'price': response.css('p.price_color::text').get(),
            'rating': response.css('p.star-rating::attr(class)').get(),
            'availability': response.css('table tr:nth-child(6) td::text').get(),
            'category': response.css('ul.breadcrumb li:nth-child(3) a::text').get(),
            'description': response.css('#product_description + p::text').get(),
            'upc': response.css('table tr:nth-child(1) td::text').get(),
            'number_of_reviews': response.css('table tr:nth-child(7) td::text').get(),
            'cover': response.css('div.item.active img::attr(src)').get(),
            'product_type': response.css('table tr:nth-child(2) td::text').get(),
        }