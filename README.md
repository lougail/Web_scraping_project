Système de veille concurrentielle pour la collecte et l'analyse de données de livres depuis books.toscrape.com.
Fonctionnalités

Web Scraping automatique de 1000+ livres avec Scrapy
Nettoyage et validation des données via pipelines
Stockage en base de données SQLite avec SQLAlchemy
API REST avec FastAPI (Clean Architecture)
Analyses statistiques (prix moyens, top catégories, etc.)

Architecture
books-intelligence/
├── books_scraper/          # Projet Scrapy
│   ├── spiders/           # Spider de scraping
│   ├── pipelines.py       # Nettoyage des données
│   └── database/          # Modèles et connexion DB
└── app/                    # API FastAPI (Clean Architecture)
    ├── routers/           # Endpoints HTTP
    ├── services/          # Logique métier
    ├── repositories/      # Accès données
    ├── schemas/           # Validation Pydantic
    └── database/          # Configuration DB
Installation
Prérequis

Python 3.11+
Git

Étapes
bash# Cloner le repository
git clone https://github.com/lougail/Web_scraping_project.git
cd Web_scraping_project

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -e .
Utilisation
1. Lancer le scraping
bashcd books_scraper
scrapy crawl books
Résultat : environ 1000 livres scrapés et sauvegardés dans books_scraper/books.db
2. Lancer l'API
bash# Depuis la racine du projet
uvicorn app.main:app --reload

API disponible : http://127.0.0.1:8000
Documentation interactive : http://127.0.0.1:8000/docs

Endpoints API
Livres

GET /books - Liste paginée de livres (params: page, per_page, category)
GET /books/{id} - Détails d'un livre

Statistiques

GET /stats/general - Statistiques générales (total livres, prix moyen)
GET /stats/top-categories - Top catégories par nombre de livres
GET /stats/price-by-category - Prix moyen par catégorie

Exemples
bash# Liste des 20 premiers livres
curl http://localhost:8000/books

# Livres de la catégorie Fiction
curl http://localhost:8000/books?category=Fiction

# Prix moyen de tous les livres
curl http://localhost:8000/stats/general

# Top 10 catégories
curl http://localhost:8000/stats/top-categories?limit=10
Données collectées
Pour chaque livre :

Titre, Prix, Notation (1-5 étoiles)
Catégorie, Description
Stock disponible
UPC (identifiant unique)
Nombre de reviews
URL de la couverture

Stack Technique

Scraping : Scrapy 2.11+
Base de données : SQLite + SQLAlchemy 2.0
API : FastAPI 0.104+
Validation : Pydantic 2.0
Server : Uvicorn

Principes d'architecture

Clean Architecture : Séparation des couches (Router → Service → Repository → Model)
Dependency Injection : FastAPI Dependencies
Repository Pattern : Abstraction de l'accès aux données
Validation : Pydantic schemas pour les entrées/sorties

Licence
MIT
Auteur
Projet réalisé dans le cadre de la certification RNCP Développeur en Intelligence Artificielle (2023)