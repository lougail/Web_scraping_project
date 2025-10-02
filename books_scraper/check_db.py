from books_scraper.database import get_session, Book
from books_scraper.database.queries import get_average_price, get_top_categories, get_average_price_by_category

# Test 1 : Prix moyen
avg_price = get_average_price()
print(f"💰 Prix moyen : {avg_price}€")

# Test 2 : Top catégories
print(f"\n📊 Top 5 catégories :")
top_cats = get_top_categories(limit=5)
for cat in top_cats:
    print(f"  - {cat['category']}: {cat['count']} livres")
    
# Test 3 : Prix moyen par catégorie
print("\n💰 Prix moyen par catégorie (top 5) :")
avg_by_cat = get_average_price_by_category()[:5]  # Juste les 5 premiers
for cat in avg_by_cat:
    print(f"  - {cat['category']}: {cat['avg_price']}€")