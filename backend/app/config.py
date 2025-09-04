from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings - can be PostgreSQL or SQLite
    DATABASE_URL: str | None = None  # For SQLite: sqlite:///./data/lawgpt.db
    
    # PostgreSQL settings (used if DATABASE_URL is not provided)
    POSTGRES_USER: str = "lawgpt"
    POSTGRES_PASSWORD: str = "lawgpt"
    POSTGRES_DB: str = "lawgpt"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    SECRET_KEY: str = "replace_me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    STORAGE_DIR: str = "uploads"
    APP_ENV: str = "dev"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()