from typing import Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    review_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("reviews.id", ondelete="SET NULL"), nullable=True
    )
    feedback_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("feedback_units.id", ondelete="SET NULL"), nullable=True
    )

    evidence_type: Mapped[str] = mapped_column(String(50), default="representative_review")
    evidence_text: Mapped[str] = mapped_column(Text)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    incident = relationship("Incident", back_populates="evidence")
