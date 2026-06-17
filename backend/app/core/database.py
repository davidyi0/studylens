"""SQLAlchemy engine + session wiring.

The `get_db()` dependency yields one session per request and guarantees it's
closed afterward, even if the handler raises. Models and real queries arrive in
Milestone 1; for M0 this just gives `/health` a connection to ping.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# `pool_pre_ping` transparently checks a connection is alive before handing it
# out, so a Postgres restart doesn't surface as a stale-connection error.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models. Lives here (next to the engine) so
    models import `Base` and Alembic imports both without a circular dependency."""



def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
