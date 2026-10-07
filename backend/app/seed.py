"""Seeds the one local demo account. Run with `python -m app.seed` after migrations.

This creates a single demo-only login (no real user data, no financial data behind it) so
graders/judges can log in without creating an account. Credentials come from .env
(DEMO_USER_EMAIL / DEMO_USER_PASSWORD) and are documented in .env.example / README.md.
"""

import logging

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_demo_user() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.demo_user_email).first()
        if existing:
            logger.info("Demo user %s already exists, skipping.", settings.demo_user_email)
            return

        user = User(
            email=settings.demo_user_email,
            hashed_password=hash_password(settings.demo_user_password),
            full_name="Flipkart Enterprise Admin",
        )
        db.add(user)
        db.commit()
        logger.info("Seeded demo user %s", settings.demo_user_email)
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_user()
