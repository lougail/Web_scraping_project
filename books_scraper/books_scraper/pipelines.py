import re
from itemadapter import ItemAdapter
from books_scraper.database import get_session, Book, init_db
from sqlalchemy.exc import IntegrityError

class DataCleaningPipeline:
    """Pipeline to clean the data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Clean the price
        if adapter.get('price'):
            adapter['price'] = float(adapter['price'].replace('£', ''))
        
        # Clean the rating
        if adapter.get('rating'):
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating_text = adapter['rating'].split()[-1]
            adapter['rating'] = rating_map.get(rating_text, 0)
            
        # Clean the availability -> stock
        if adapter.get('availability'):
            avail_text = adapter['availability']
            match = re.search(r'\((\d+) available\)', avail_text)
            adapter['stock'] = int(match.group(1)) if match else 0
            del adapter['availability']
            
        # Clean the number_of_reviews
        if adapter.get('number_of_reviews'):
            adapter['number_of_reviews'] = int(adapter['number_of_reviews'])

        # Clean the title
        if adapter.get('title'):
            adapter['title'] = adapter['title'].strip()

        # Clean the description
        if adapter.get('description'):
            adapter['description'] = adapter['description'].strip()
            
        # Clean the cover (construire l'URL complète)
        if adapter.get('cover'):
            cover_relative = adapter['cover']  # "../../media/cache/..."
            # Construire l'URL complète
            adapter['cover'] = f"http://books.toscrape.com/{cover_relative.replace('../../', '')}"
        
        return item
    
from books_scraper.database import get_session, Book, init_db
from sqlalchemy.exc import IntegrityError
from itemadapter import ItemAdapter

class DatabasePipeline:
    """Pipeline pour sauvegarder en base de données"""
    
    def open_spider(self, spider):
        """Appelé quand le spider démarre"""
        init_db()
        self.session = get_session()
    
    def close_spider(self, spider):
        """Appelé quand le spider se termine"""
        self.session.close()
    
    def process_item(self, item, spider):
        """Sauvegarder chaque item en base"""
        adapter = ItemAdapter(item)
        
        book = Book(
            upc=adapter.get('upc'),
            title=adapter.get('title'),
            price=adapter.get('price'),
            rating=adapter.get('rating'),
            stock=adapter.get('stock'),
            category=adapter.get('category'),
            description=adapter.get('description'),
            number_of_reviews=adapter.get('number_of_reviews'),
            cover=adapter.get('cover'),
            product_type=adapter.get('product_type')
        )
        
        try:
            self.session.add(book)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            spider.logger.warning(f"Doublon ignoré : {adapter.get('upc')}")
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"Erreur lors de l'insertion : {e}")
        
        return item