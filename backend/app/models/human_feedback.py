from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HumanFeedback(Base):
    __tablename__ = "human_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("themes.id", ondelete="CASCADE"), nullable=True, index=True
    )
    feedback_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("feedback_units.id", ondelete="CASCADE"), nullable=True, index=True
    )

    old_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    new_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_action: Mapped[str] = mapped_column(String(50))
    # correct | merge | split | ignore | approve | reject

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
