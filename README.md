# Web Scraping Project — Système de veille concurrentielle

## 🎯 Description

Ce projet est un système de veille concurrentielle centré sur la collecte et l’analyse de données issues d’un site de livres ([books.toscrape.com](https://books.toscrape.com)).  
Il combine un composant de **scraping** (via Scrapy) et une **API REST** (via FastAPI) pour exposer les données collectées et proposer des statistiques.

### Fonctionnalités principales

- Scraping automatique de plus de **1000 livres** à partir de *books.toscrape.com*  
- Nettoyage et validation des données via pipelines Scrapy  
- Stockage dans une base de données **SQLite** via **SQLAlchemy**  
- API REST (FastAPI) structurée selon les principes de la Clean Architecture  
- Endpoints de consultation des livres + endpoints de statistiques (moyennes, top catégories, etc.)  

---

## 📁 Architecture du projet

```
books-intelligence/
├── books_scraper/        # Projet Scrapy
│   ├── spiders/           # Les spiders pour le scraping
│   ├── pipelines.py       # Nettoyage, validation, insertion en DB
│   └── database/          # Modèles SQLAlchemy & gestion DB
└── app/                   # API FastAPI (Clean Architecture)
    ├── routers/           # Définition des routes HTTP / endpoints
    ├── services/          # Logique métier (cas d’usage)
    ├── repositories/      # Accès aux données / abstraction DB
    ├── schemas/           # Modèles Pydantic (validation)
    └── database/          # Configuration de la connexion DB
```

---

## 🔧 Prérequis

- Python 3.11 ou supérieur  
- Git  
- (Optionnel mais recommandé) un environnement virtuel  

---

## 🚀 Installation & utilisation

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

### 4. Lancer l’API FastAPI
Depuis la racine du projet :
```bash
uvicorn app.main:app --reload
```
- API disponible : [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- Documentation interactive : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  

---

## 🧰 Endpoints de l’API

### Livres
- `GET /books` : liste paginée de livres (`page`, `per_page`, `category`)  
- `GET /books/{id}` : détails d’un livre

### Statistiques
- `GET /stats/general` : statistiques globales (nb de livres, prix moyen, etc.)  
- `GET /stats/top-categories` : top catégories par nombre de livres  
- `GET /stats/price-by-category` : prix moyen par catégorie  

#### Exemples avec `curl`
```bash
# Obtenir les 20 premiers livres
curl http://localhost:8000/books

# Filtrer par catégorie “Fiction”
curl http://localhost:8000/books?category=Fiction

# Obtenir le prix moyen
curl http://localhost:8000/stats/general

# Top 10 catégories
curl http://localhost:8000/stats/top-categories?limit=10
```

---

## 📊 Structure des données collectées

- Titre  
- Prix  
- Note (1 à 5 étoiles)  
- Catégorie  
- Description  
- Stock disponible  
- UPC (identifiant unique)  
- Nombre de reviews  
- URL de l’image (couverture)  

---

## 🧩 Stack technique

- **Scraping** : Scrapy  
- **Base de données** : SQLite + SQLAlchemy  
- **API** : FastAPI  
- **Validation** : Pydantic  
- **Serveur** : Uvicorn  

---

## 🏛️ Principes d’architecture

- **Clean Architecture** : séparation claire des couches (routers → services → repositories → modèles)  
- **Injection de dépendances** (via FastAPI)  
- **Repository Pattern** pour abstraire l’accès aux données  
- **Validation stricte** via Pydantic  

---

## 🧾 Licence

Ce projet est distribué sous licence **MIT**.  
Auteur : Lougail  

---

## 📌 Améliorations possibles

- Ajout de tests unitaires et d’intégration  
- Scraping multi-sources (plusieurs sites de livres)  
- Planification automatisée (cron, Airflow, etc.)  
- Authentification et gestion des rôles sur l’API  
- Migration vers une base plus robuste (PostgreSQL)  
- Déploiement en production (Docker, cloud, CI/CD)  
