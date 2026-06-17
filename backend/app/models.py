"""SQLAlchemy ORM models — the five tables from the StudyLens schema.

All in one module while the schema is small and tightly related; split into a
`models/` package later only if it grows. SQLAlchemy 2.0 typed style
(`Mapped` / `mapped_column`). Mirrors the DDL in StudyLens_Project_Roadmap.md.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

_uuid_pk = lambda: mapped_column(
    UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # Placeholder until wires up real bcrypt hashing.
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    courses: Mapped[list["Course"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    # The per-course ChromaDB collection name (multi-course isolation, M3/M4).
    chroma_collection_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="courses")
    documents: Mapped[list["Document"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = _uuid_pk()
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    # Lifecycle: pending -> processing -> complete | failed
    status: Mapped[str] = mapped_column(String(50), server_default="pending")
    chunk_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    course: Mapped["Course"] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = _uuid_pk()
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chroma_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    chunk_index: Mapped[int | None] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    document: Mapped["Document"] = relationship(back_populates="chunks")


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = _uuid_pk()
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list | None] = mapped_column(JSONB)
    was_cached: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
