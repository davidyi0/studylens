"""Seed one dev user + course so M2/M4 have valid ids before auth (M6) exists.

Idempotent: re-running is a no-op once the dev user is present. Run with:
    docker compose exec api python -m scripts.seed
"""
import uuid

from app.core.database import SessionLocal
from app.models import Course, User

DEV_EMAIL = "dev@studylens.local"
# Placeholder until M6 replaces this with a real bcrypt hash.
DEV_PASSWORD_HASH = "placeholder-not-a-real-hash"


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter_by(email=DEV_EMAIL).first():
            print(f"Dev user {DEV_EMAIL} already exists — nothing to do.")
            return

        user = User(email=DEV_EMAIL, password_hash=DEV_PASSWORD_HASH)
        db.add(user)
        db.flush()  # assigns user.id (server-side default) without committing

        # Generate the course id client-side so the Chroma collection name can
        # follow the `course_{course_id}` convention the M3/M4 pipeline expects.
        course_id = uuid.uuid4()
        course = Course(
            id=course_id,
            user_id=user.id,
            name="CS 161 — Algorithms",
            description="Seed course for local development.",
            chroma_collection_id=f"course_{course_id}",
        )
        db.add(course)
        db.commit()
        print(f"Seeded user {user.id} and course {course_id}.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
