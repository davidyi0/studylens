"""Centralized application settings.

Every environment-dependent value flows through this one `Settings` object so the
rest of the app never reads `os.environ` directly. Pydantic validates types and
raises on startup if a required value is missing — fail loud, fail early.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Connection strings (defaults match docker-compose service names).
    DATABASE_URL: str = "postgresql+psycopg://studylens:studylens@postgres:5432/studylens"
    REDIS_URL: str = "redis://redis:6379/0"
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000

    # Only required once ingestion/query land (M3/M4). Optional for M0 boot.
    OPENAI_API_KEY: str | None = None

    # CORS origin for the Vite dev server.
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Import this singleton everywhere; instantiated once at process start.
settings = Settings()
