from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")
    # uploaded -> processing -> processed -> failed
    processing_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    processing_progress: Mapped[float] = mapped_column(Float, default=0.0)
    processing_error: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    reviews = relationship("Review", back_populates="dataset", cascade="all, delete-orphan")
    themes = relationship("Theme", back_populates="dataset", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="dataset", cascade="all, delete-orphan")
