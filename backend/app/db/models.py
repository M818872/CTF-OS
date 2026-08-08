from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200))
    challenge_type: Mapped[str] = mapped_column(String(50), default="unknown")
    status: Mapped[str] = mapped_column(String(30), default="created")
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    activities: Mapped[list[InvestigationActivity]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan", order_by="InvestigationActivity.created_at"
    )
    evidence: Mapped[list[Evidence]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan", order_by="Evidence.created_at"
    )
    artifacts: Mapped[list[Artifact]] = relationship(
        back_populates="investigation", cascade="all, delete-orphan", order_by="Artifact.created_at"
    )


class InvestigationActivity(Base):
    __tablename__ = "investigation_activities"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investigation_id: Mapped[UUID] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="planned")
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    investigation: Mapped[Investigation] = relationship(back_populates="activities")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investigation_id: Mapped[UUID] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(50), default="observation")
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100), default="agent")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    investigation: Mapped[Investigation] = relationship(back_populates="evidence")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investigation_id: Mapped[UUID] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    storage_key: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    investigation: Mapped[Investigation] = relationship(back_populates="artifacts")
