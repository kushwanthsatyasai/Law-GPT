from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings
import os

# Check if DATABASE_URL is provided in environment (for SQLite support)
if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
    # Ensure directory exists for SQLite
    if DATABASE_URL.startswith('sqlite'):
        db_path = DATABASE_URL.replace('sqlite:///', '')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
else:
    # Default to PostgreSQL
    DATABASE_URL = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()