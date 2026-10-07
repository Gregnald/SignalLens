import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.database import Base, engine


def _db_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except OperationalError:
        return False


DB_AVAILABLE = _db_available()
requires_db = pytest.mark.skipif(
    not DB_AVAILABLE, reason="PostgreSQL (with pgvector) is not reachable from this environment"
)


@pytest.fixture()
def db_session():
    """Yields a Session wrapped in an outer transaction that's always rolled back, even
    though the service code under test calls db.commit() itself (every commit lands on
    a SAVEPOINT via join_transaction_mode, not the real outer transaction) — so running
    the suite against a real database (e.g. docker compose's Postgres) never leaves
    fixture rows behind, no matter what the code under test commits.
    """
    if not DB_AVAILABLE:
        pytest.skip("database not available")
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    outer_transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()
