from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Ajouter le parent au path pour importer config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config import DATABASE_URL

# Create the database engine
engine = create_engine(DATABASE_URL, echo=False)  # echo=False en production

# Base for the models
Base = declarative_base()

# Session to interact with the database
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """Get a session of the database"""
    return SessionLocal()

def init_db():
    """Create all the tables""" 
    from books_scraper.database.models import Book
    Base.metadata.create_all(engine)