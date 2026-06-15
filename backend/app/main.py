"""StudyLens API entrypoint (Milestone 0).

Exposes a single `/health` endpoint that verifies the API can actually reach its
dependencies (Postgres + ChromaDB), not just that the process is alive. Routers
for auth/courses/documents/query are added in later milestones.
"""
import chromadb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

app = FastAPI(title="StudyLens API", version="0.1.0")

# Allow the Vite dev server to call the API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _check_postgres() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _check_chroma() -> bool:
    try:
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        client.heartbeat()
        return True
    except Exception:
        return False


@app.get("/health")
def health() -> dict:
    """Readiness check: reports per-dependency status so a red light is diagnosable."""
    checks = {"postgres": _check_postgres(), "chroma": _check_chroma()}
    status = "ok" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
