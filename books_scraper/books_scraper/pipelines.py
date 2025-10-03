"""Pipelines Scrapy pour le nettoyage et la sauvegarde des données.

Ce module contient les pipelines qui traitent les items extraits par le spider :
- DataCleaningPipeline : nettoie et transforme les données brutes
- DatabasePipeline : sauvegarde les données nettoyées en base de données avec historique
"""

import re
from datetime import datetime, timezone
from itemadapter import ItemAdapter
from books_scraper.books_scraper.database import get_session, Book, init_db
from books_scraper.books_scraper.constants import RATING_MAP, BASE_URL, DEFAULT_RATING, DEFAULT_STOCK, DEFAULT_REVIEWS
from sqlalchemy.exc import IntegrityError


class DataCleaningPipeline:
    """Pipeline de nettoyage et transformation des données scrapées.

    Ce pipeline transforme les données brutes extraites du HTML en données
    structurées et typées prêtes pour la base de données :
    - Conversion des prix (£25.99 -> 25.99)
    - Conversion des notes textuelles (Three -> 3)
    - Extraction du stock depuis le texte de disponibilité
    - Nettoyage des espaces dans les textes
    - Construction des URLs complètes des images

    Example:
        Configuré automatiquement dans settings.py :
        ITEM_PIPELINES = {
            'books_scraper.pipelines.DataCleaningPipeline': 100,
        }
    """

    def process_item(self, item, spider):
        """Nettoie et transforme un item scraté.

        Args:
            item (dict): Données brutes extraites par le spider
            spider (scrapy.Spider): Instance du spider (pour le logging)

        Returns:
            dict: Item nettoyé et transformé

        Note:
            Cette méthode est appelée automatiquement pour chaque item extrait par le spider.
        """
        adapter = ItemAdapter(item)

        # Nettoyer le prix : "£25.99" -> 25.99
        if adapter.get("price"):
            try:
                adapter["price"] = float(adapter["price"].replace("£", ""))
            except (ValueError, AttributeError) as e:
                spider.logger.warning(f"Prix invalide : {adapter.get('price')} - {e}")
                adapter["price"] = 0.0

        # Nettoyer la note : "star-rating Three" -> 3
        if adapter.get("rating"):
            try:
                rating_text = adapter["rating"].split()[-1]
                adapter["rating"] = RATING_MAP.get(rating_text, DEFAULT_RATING)
            except (IndexError, AttributeError) as e:
                spider.logger.warning(f"Note invalide : {adapter.get('rating')} - {e}")
                adapter["rating"] = DEFAULT_RATING

        # Extraire le stock depuis la disponibilité : "In stock (22 available)" -> 22
        if adapter.get("availability"):
            try:
                avail_text = adapter["availability"]
                match = re.search(r"\((\d+) available\)", avail_text)
                adapter["stock"] = int(match.group(1)) if match else DEFAULT_STOCK
            except (ValueError, AttributeError) as e:
                spider.logger.warning(f"Stock invalide : {adapter.get('availability')} - {e}")
                adapter["stock"] = DEFAULT_STOCK
            del adapter["availability"]

        # Nettoyer le nombre de reviews : "0" -> 0
        if adapter.get("number_of_reviews"):
            try:
                adapter["number_of_reviews"] = int(adapter["number_of_reviews"])
            except (ValueError, TypeError) as e:
                spider.logger.warning(f"Nombre de reviews invalide : {adapter.get('number_of_reviews')} - {e}")
                adapter["number_of_reviews"] = DEFAULT_REVIEWS

        # Nettoyer le titre (supprimer les espaces superflus)
        if adapter.get("title"):
            adapter["title"] = adapter["title"].strip()

        # Nettoyer la description (supprimer les espaces superflus)
        if adapter.get("description"):
            adapter["description"] = adapter["description"].strip()

        # Construire l'URL complète de la couverture
        # "../../media/cache/..." -> "http://books.toscrape.com/media/cache/..."
        if adapter.get("cover"):
            try:
                cover_relative = adapter["cover"]
                adapter["cover"] = f"{BASE_URL}/{cover_relative.replace('../../', '')}"
            except (AttributeError, TypeError) as e:
                spider.logger.warning(f"URL de couverture invalide : {adapter.get('cover')} - {e}")
                adapter["cover"] = None

        return item


class DatabasePipeline:
    """Pipeline de sauvegarde des données en base de données SQLite avec historique.

    Ce pipeline prend les items nettoyés et les insère/met à jour dans la base de données.
    Il gère automatiquement l'historique des changements (prix, stock, rating, reviews).

    Attributes:
        session (Session): Session SQLAlchemy pour les opérations DB

    Example:
        Configuré automatiquement dans settings.py :
        ITEM_PIPELINES = {
            'books_scraper.pipelines.DatabasePipeline': 200,
        }

    Note:
        La base de données est initialisée au démarrage du spider
        et la session est fermée à la fin.
    """

    def open_spider(self, spider):
        """Initialise la base de données et crée une session au démarrage du spider.

        Args:
            spider (scrapy.Spider): Instance du spider qui démarre

        Note:
            Appelé automatiquement une seule fois au début du crawl.
        """
        init_db()
        self.session = get_session()

    def close_spider(self, spider):
        """Ferme proprement la session de base de données à la fin du spider.

        Args:
            spider (scrapy.Spider): Instance du spider qui se termine

        Note:
            Appelé automatiquement une seule fois à la fin du crawl.
        """
        self.session.close()

    def process_item(self, item, spider):
        """Sauvegarde un item nettoyé en base de données et track l'historique.

        Créer ou met à jour un objet Book SQLAlchemy à partir de l'item.
        Si des changements sont détectés (prix, stock, rating, reviews), crée une entrée historique.

        Args:
            item (dict): Item nettoyé par DataCleaningPipeline
            spider (scrapy.Spider): Instance du spider (pour le logging)

        Returns:
            dict: L'item original (pour chaînage de pipelines éventuel)

        Note:
            - Nouveau livre → créé + entrée historique
            - Livre existant sans changement → rien
            - Livre existant avec changement → mise à jour + entrée historique
        """
        adapter = ItemAdapter(item)
        upc = adapter.get("upc")

        try:
            # Récupérer le livre existant
            existing_book = self.session.query(Book).filter_by(upc=upc).first()

            if existing_book:
                # Livre existant : vérifier les changements
                has_changes = (
                    existing_book.price != adapter.get("price") or
                    existing_book.stock != adapter.get("stock") or
                    existing_book.rating != adapter.get("rating") or
                    existing_book.number_of_reviews != adapter.get("number_of_reviews")
                )

                if has_changes:
                    # Créer une entrée historique avec les nouvelles valeurs
                    from books_scraper.books_scraper.database.models import BookHistory

                    history = BookHistory(
                        book_id=existing_book.id,
                        upc=existing_book.upc,
                        price=adapter.get("price"),
                        stock=adapter.get("stock"),
                        rating=adapter.get("rating"),
                        number_of_reviews=adapter.get("number_of_reviews"),
                        scraped_at=datetime.now(timezone.utc)
                    )
                    self.session.add(history)

                    # Mettre à jour le livre
                    existing_book.price = adapter.get("price")
                    existing_book.stock = adapter.get("stock")
                    existing_book.rating = adapter.get("rating")
                    existing_book.number_of_reviews = adapter.get("number_of_reviews")
                    existing_book.last_updated = datetime.now(timezone.utc)

                    self.session.commit()
                    spider.logger.info(f"Livre mis a jour avec historique: {upc}")
                else:
                    spider.logger.debug(f"Aucun changement pour: {upc}")

            else:
                # Nouveau livre : créer + ajouter à l'historique
                book = Book(
                    upc=upc,
                    title=adapter.get("title"),
                    price=adapter.get("price"),
                    rating=adapter.get("rating"),
                    stock=adapter.get("stock"),
                    category=adapter.get("category"),
                    description=adapter.get("description"),
                    number_of_reviews=adapter.get("number_of_reviews"),
                    cover=adapter.get("cover"),
                    product_type=adapter.get("product_type"),
                )
                self.session.add(book)
                self.session.flush()  # Pour obtenir book.id

                # Créer la première entrée historique
                from books_scraper.books_scraper.database.models import BookHistory

                history = BookHistory(
                    book_id=book.id,
                    upc=book.upc,
                    price=book.price,
                    stock=book.stock,
                    rating=book.rating,
                    number_of_reviews=book.number_of_reviews,
                    scraped_at=datetime.now(timezone.utc)
                )
                self.session.add(history)
                self.session.commit()
                spider.logger.info(f"Nouveau livre cree avec historique: {upc}")

        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"Erreur lors du traitement de {upc}: {e}")

        return item
