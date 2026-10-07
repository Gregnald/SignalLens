"""add product fields to reviews

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("reviews", sa.Column("product_name", sa.String(500)))
    op.add_column("reviews", sa.Column("product_category", sa.String(100)))
    op.add_column("reviews", sa.Column("product_price", sa.Float))
    op.create_index("ix_reviews_product_name", "reviews", ["product_name"])
    op.create_index("ix_reviews_product_category", "reviews", ["product_category"])


def downgrade() -> None:
    op.drop_index("ix_reviews_product_category", table_name="reviews")
    op.drop_index("ix_reviews_product_name", table_name="reviews")
    op.drop_column("reviews", "product_price")
    op.drop_column("reviews", "product_category")
    op.drop_column("reviews", "product_name")
