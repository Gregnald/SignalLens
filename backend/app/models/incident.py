from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    severity: Mapped[str] = mapped_column(String(20), default="low")
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)

    first_detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    growth_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    likely_driver: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    root_cause_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    affected_platforms: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    affected_versions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    affected_devices: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    recommended_owner: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recommended_priority: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="open")

    action_report: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    dataset = relationship("Dataset", back_populates="incidents")
    theme = relationship("Theme", back_populates="incidents")
    evidence = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
