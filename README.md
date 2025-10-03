# Web Scraping Project — Système de veille concurrentielle

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🎯 Description

Ce projet est un système de veille concurrentielle centré sur la collecte et l’analyse de données issues d’un site de livres ([books.toscrape.com](https://books.toscrape.com)).  
Il combine un composant de **scraping** (via Scrapy) et une **API REST** (via FastAPI) pour exposer les données collectées et proposer des statistiques avancées.

---

## 🚀 Fonctionnalités principales

- Scraping automatique de plus de **1000 livres** à partir de *books.toscrape.com*
- Nettoyage et validation des données via pipelines Scrapy
- Stockage dans une base de données **SQLite** via **SQLAlchemy**
- **Système d'historique** : tracking automatique des changements de prix, stock, rating et reviews
- API REST (FastAPI) structurée selon les principes de la Clean Architecture
- **Recherche avancée** : multi-critères avec filtres (prix, rating, catégorie, texte)
- **Endpoints d'historique** : évolution des prix, alertes stock, changements récents
- Endpoints de statistiques avancées (distribution des notes, tranches de prix, etc.)
- **Rate limiting** et middleware (CORS, compression GZip)
- Pagination complète avec métadonnées (total, pages, etc.)
- Tri et ordonnancement dynamiques
- Documentation interactive complète (Swagger UI)

---

## 🏗️ Architecture du projet

```
books-intelligence/
├── books_scraper/         # Projet Scrapy : scraping & nettoyage
│   ├── books_scraper/
│   │   ├── spiders/       # Les spiders pour le scraping
│   │   ├── pipelines.py   # Nettoyage, validation, insertion en DB + historique
│   │   ├── settings.py    # Paramétrage Scrapy (throttling, cache, etc.)
│   │   ├── constants.py   # Constantes (RATING_MAP, URLs, etc.)
│   │   └── database/      # Modèles SQLAlchemy & gestion DB
│   └── books.db           # Base de données SQLite
├── app/                   # API FastAPI (Clean Architecture)
│   ├── routers/           # Routes HTTP / endpoints
│   │   ├── books.py       # Endpoints livres (liste, détail, search, categories, random)
│   │   ├── stats.py       # Endpoints statistiques
│   │   └── history.py     # Endpoints historique (prix, stock, changements)
│   ├── services/          # Logique métier (cas d'usage)
│   ├── repositories/      # Accès aux données / abstraction DB
│   ├── schemas/           # Modèles Pydantic (validation)
│   ├── database/          # Configuration connexion DB & modèles
│   ├── config.py          # Configuration centralisée
│   ├── error_handlers.py  # Gestion centralisée des erreurs
│   └── main.py            # Point d'entrée FastAPI
├── tests/                 # Tests unitaires et d'intégration (26 tests)
├── requirements.txt       # Dépendances Python
├── pyproject.toml         # Configuration du projet
├── Dockerfile             # Conteneurisation
├── Makefile               # Commandes automatisées
├── LICENSE
└── README.md
```

---

## ⚙️ Prérequis

- Python 3.11 ou supérieur  
- Git  
- (Optionnel mais recommandé) un environnement virtuel  
- SQLite (installé par défaut sur la plupart des systèmes)
- (Bonus) Docker pour la conteneurisation

---

## 🚦 Installation & utilisation

### 1. Cloner le dépôt

```bash
git clone https://github.com/lougail/Web_scraping_project.git
cd Web_scraping_project
```

### 2. Créer un environnement virtuel et installer les dépendances

```bash
python -m venv venv
# Sous Linux/Mac
source venv/bin/activate
# Sous Windows
venv\Scripts\activate

pip install -e .
```

### 3. Lancer le scraping

```bash
cd books_scraper
scrapy crawl books
```
➡️ Les données collectées seront stockées dans `books_scraper/books.db`.

### 4. Lancer l'API FastAPI

Depuis la racine du projet :

```bash
uvicorn app.main:app --reload
```
- API disponible : [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Documentation interactive : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. (Optionnel) Lancer les tests

```bash
pytest tests/
```

### 6. (Optionnel) Utiliser Docker

```bash
docker build -t books-intelligence .
docker run -p 8000:8000 books-intelligence
```

### 7. (Optionnel) Utiliser le Makefile

Lance les commandes d'un coup avec :

```bash
make scrape     # Lancer le scraping
make api        # Lancer l'API
make test       # Lancer les tests
make all        # Tout faire
```

---

## 📚 Endpoints de l'API

### 📖 Livres

- `GET /books` : liste paginée de livres avec tri et filtres
  - Paramètres : `page`, `per_page`, `category`, `sort_by`, `order`
- `GET /books/{id}` : détails d'un livre spécifique
- `GET /books/count` : nombre total de livres
- `GET /books/search` : recherche avancée multi-critères
  - Paramètres : `q` (texte), `category`, `min_price`, `max_price`, `min_rating`, `max_rating`, `sort_by`, `order`
- `GET /books/categories` : liste de toutes les catégories disponibles
- `GET /books/random` : obtenir des livres aléatoires
  - Paramètres : `limit` (défaut: 10, max: 50)

### 📊 Statistiques

- `GET /stats/general` : statistiques globales (nb livres, prix moyen, etc.)
- `GET /stats/top-categories` : top catégories par nombre de livres
  - Paramètres : `limit` (défaut: 10)
- `GET /stats/price-by-category` : prix moyen par catégorie
- `GET /stats/rating-distribution` : distribution des notes (1-5 étoiles)
- `GET /stats/price-ranges` : répartition des livres par tranches de prix

### 📈 Historique

- `GET /history/books/{book_id}` : historique complet d'un livre
  - Paramètres : `days` (limiter aux N derniers jours), `limit`
- `GET /history/books/{book_id}/price` : évolution du prix dans le temps
  - Paramètres : `days`
- `GET /history/price-changes` : livres avec changements de prix récents
  - Paramètres : `days` (défaut: 7), `limit` (défaut: 50)
- `GET /history/stock-alerts` : livres en rupture ou stock faible
  - Paramètres : `threshold` (défaut: 10)

### 🏥 Santé

- `GET /` : informations sur l'API et liste des endpoints
- `GET /health` : health check (status + connexion DB)

#### Exemples avec `curl`

```bash
# Liste paginée avec tri par prix croissant
curl "http://localhost:8000/books?page=1&per_page=10&sort_by=price&order=asc"

# Recherche avancée : livres "Python" entre 10€ et 50€, note ≥ 4
curl "http://localhost:8000/books/search?q=python&min_price=10&max_price=50&min_rating=4"

# Toutes les catégories disponibles
curl http://localhost:8000/books/categories

# 5 livres aléatoires
curl "http://localhost:8000/books/random?limit=5"

# Statistiques générales
curl http://localhost:8000/stats/general

# Distribution des notes
curl http://localhost:8000/stats/rating-distribution

# Historique complet d'un livre (30 derniers jours)
curl "http://localhost:8000/history/books/1?days=30"

# Évolution du prix d'un livre
curl "http://localhost:8000/history/books/1/price?days=90"

# Changements de prix des 7 derniers jours
curl "http://localhost:8000/history/price-changes?days=7&limit=20"

# Alertes stock (livres avec stock ≤ 5)
curl "http://localhost:8000/history/stock-alerts?threshold=5"
```

---

## 🗃️ Structure de la base de données

### Table `books`
- `id` : Identifiant unique (auto-incrémenté)
- `upc` : Universal Product Code (identifiant unique du livre)
- `title` : Titre du livre
- `price` : Prix (float)
- `rating` : Note de 1 à 5 étoiles (int)
- `category` : Catégorie du livre
- `description` : Description détaillée
- `stock` : Stock disponible (int)
- `number_of_reviews` : Nombre d'avis
- `image_url` : URL de l'image de couverture
- `scraped_at` : Date du dernier scraping
- `last_updated` : Date de dernière modification

### Table `book_history`
- `id` : Identifiant unique
- `book_id` : Référence au livre (foreign key)
- `upc` : UPC du livre
- `price` : Prix à ce moment
- `stock` : Stock à ce moment
- `rating` : Note à ce moment
- `number_of_reviews` : Nombre d'avis à ce moment
- `scraped_at` : Date de l'enregistrement

**Index optimisés** : book_id, upc, scraped_at, composites (book_id + scraped_at, upc + scraped_at)  

---

## 🧑‍💻 Stack technique

- **Scraping** : Scrapy 2.13
- **Base de données** : SQLite + SQLAlchemy 2.0
- **API** : FastAPI 0.115
- **Validation** : Pydantic 2.10 + Pydantic Settings
- **Serveur** : Uvicorn 0.34
- **Rate Limiting** : SlowAPI (in-memory)
- **Middleware** : CORS, GZip compression
- **Tests** : Pytest 7.4 + httpx + pytest-asyncio (26 tests)
- **Linting/formatting** : Black, Ruff
- **Conteneurisation** : Docker

---

## 🏛️ Principes d'architecture

- **Clean Architecture** : séparation claire des couches (routers → services → repositories → modèles)
- **Injection de dépendances** (via FastAPI)
- **Repository Pattern** pour abstraire l'accès aux données
- **Validation stricte** via Pydantic avec schémas typés
- **Logging** et gestion d'erreurs centralisée
- **Pagination avancée** avec métadonnées (total, pages, etc.)
- **Rate limiting** pour protection anti-abus
- **Historique automatique** : tracking des changements en temps réel via pipeline
- **Index DB optimisés** : composite indexes pour queries performantes
- **Code modulaire** : chaque couche a sa responsabilité unique

---

## 🥇 Bonnes pratiques et automatisation

- **Formatage & lint** :  
  - Formater le code : `black .`
  - Linter le code : `ruff .`
- **Tests** :  
  - Lancer les tests unitaires : `pytest tests/`
- **Automatisation** (si Makefile présent) :  
  - Scraping + API + tests : `make all`

---

## 🧑‍🔬 Améliorations possibles

- 🔄 Scraping multi-sources (plusieurs sites de livres)
- ⏰ Planification automatisée (cron, Airflow, Celery pour scraping périodique)
- 🔐 Authentification JWT et gestion des rôles (admin, user)
- 🗄️ Migration vers PostgreSQL pour production
- ☁️ Déploiement cloud (AWS/Azure/GCP) avec CI/CD (GitHub Actions)
- 📊 Dashboard frontend (React/Vue) pour visualiser les données
- 🔍 Search engine (Elasticsearch) pour recherche full-text avancée
- 📧 Système de notifications (email/webhook) pour alertes prix/stock
- 📈 Monitoring et observabilité (Prometheus/Grafana, Sentry)
- 🚀 Caching distribué (Redis) pour améliorer les performances
- 📝 Webhooks pour événements (nouveau livre, changement prix, etc.)

---

## 📝 Licence

Ce projet est distribué sous licence **MIT**.  
Auteur : Lougail

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Proposez une issue ou une pull request pour discuter de vos idées ou corrections.  
Voir `CONTRIBUTING.md` (à créer pour les guidelines de contribution).

---