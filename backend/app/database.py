from sqlalchemy import create_engine, text
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
    # Default to PostgreSQL with psycopg3 driver
    DATABASE_URL = (
        f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

# Handle different PostgreSQL URL formats and ensure we use psycopg3
if DATABASE_URL.startswith('postgresql://') and not DATABASE_URL.startswith('postgresql+psycopg://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
elif DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://')

try:
    engine = create_engine(DATABASE_URL)
    # Test the connection and enable pgvector extension for PostgreSQL
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        # Enable pgvector extension if using PostgreSQL
        if not DATABASE_URL.startswith('sqlite'):
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                print("✅ pgvector extension enabled")
            except Exception as e:
                print(f"⚠️  Could not enable pgvector extension: {e}")
                print("   This may require superuser privileges on the database")
    print(f"✅ Database connected successfully: {DATABASE_URL.split('@')[0]}@***")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    # Fallback to SQLite for development
    if not DATABASE_URL.startswith('sqlite'):
        print("🔄 Falling back to SQLite database...")
        os.makedirs('data', exist_ok=True)
        DATABASE_URL = 'sqlite:///./data/lawgpt.db'
        engine = create_engine(DATABASE_URL)
        print(f"✅ SQLite database initialized: {DATABASE_URL}")
    else:
        raise e

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()