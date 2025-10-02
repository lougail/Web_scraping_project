from sqlalchemy import func
from books_scraper.database import get_session, Book

def get_total_books():
    """Nombre total de livres"""
    session = get_session()
    count = session.query(Book).count()
    session.close()
    return count

def get_average_price():
    """Prix moyen de tous les livres"""
    session = get_session()
    result = session.query(func.avg(Book.price)).scalar()  # .scalar() pour avoir juste le nombre
    session.close()
    return round(result, 2) if result else 0  # Arrondir à 2 décimales

def get_top_categories(limit=10):
    """Top catégories avec le plus de livres"""
    session = get_session()
    
    results = session.query(
        Book.category,
        func.count(Book.id).label('count')
    ).group_by(Book.category)\
     .order_by(func.count(Book.id).desc())\
     .limit(limit)\
     .all()
    
    session.close()
    
    # Formater en liste de dictionnaires (plus facile à utiliser)
    return [{'category': r[0], 'count': r[1]} for r in results]

def get_average_price_by_category():
    session = get_session()
    
    results = session.query(
        Book.category,
        func.avg(Book.price).label('avg_price')
    ).group_by(Book.category)\
     .order_by(func.avg(Book.price).desc())\
     .all()
    
    session.close()
    return [{'category': r[0], 'avg_price': round(r[1], 2)} for r in results]