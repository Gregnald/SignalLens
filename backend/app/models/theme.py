from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cluster_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    volume: Mapped[int] = mapped_column(Integer, default=0)
    growth_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    avg_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    negative_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    impact_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_emerging: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    dataset = relationship("Dataset", back_populates="themes")
    feedback_units = relationship("FeedbackUnit", back_populates="theme")
    incidents = relationship("Incident", back_populates="theme", cascade="all, delete-orphan")
