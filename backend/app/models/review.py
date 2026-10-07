from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)
    external_review_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    raw_text: Mapped[str] = mapped_column(Text)
    clean_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    app_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    device: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    product_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    product_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    product_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_group_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    integrity_risk: Mapped[float] = mapped_column(Float, default=0.0)
    rating_text_conflict: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    dataset = relationship("Dataset", back_populates="reviews")
    feedback_units = relationship(
        "FeedbackUnit", back_populates="review", cascade="all, delete-orphan"
    )
