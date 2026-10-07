"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBEDDING_DIM = 384


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, server_default="Demo User"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source", sa.String(255)),
        sa.Column("file_name", sa.String(255)),
        sa.Column("total_reviews", sa.Integer, server_default="0"),
        sa.Column("status", sa.String(50), server_default="uploaded"),
        sa.Column("processing_stage", sa.String(100)),
        sa.Column("processing_progress", sa.Float, server_default="0.0"),
        sa.Column("processing_error", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "dataset_id",
            sa.Integer,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_review_id", sa.String(255)),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("clean_text", sa.Text),
        sa.Column("rating", sa.Float),
        sa.Column("review_date", sa.Date),
        sa.Column("app_version", sa.String(50)),
        sa.Column("platform", sa.String(50)),
        sa.Column("device", sa.String(100)),
        sa.Column("country", sa.String(100)),
        sa.Column("language", sa.String(10)),
        sa.Column("source", sa.String(100)),
        sa.Column("is_duplicate", sa.Boolean, server_default=sa.false()),
        sa.Column("duplicate_group_id", sa.Integer),
        sa.Column("integrity_risk", sa.Float, server_default="0.0"),
        sa.Column("rating_text_conflict", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reviews_dataset_id", "reviews", ["dataset_id"])
    op.create_index("ix_reviews_duplicate_group_id", "reviews", ["duplicate_group_id"])

    op.create_table(
        "themes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "dataset_id",
            sa.Integer,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("description", sa.Text),
        sa.Column("cluster_id", sa.Integer),
        sa.Column("volume", sa.Integer, server_default="0"),
        sa.Column("growth_percent", sa.Float),
        sa.Column("avg_sentiment", sa.Float),
        sa.Column("negative_percent", sa.Float),
        sa.Column("severity", sa.String(20)),
        sa.Column("impact_score", sa.Float),
        sa.Column("confidence", sa.Float),
        sa.Column("is_emerging", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_themes_dataset_id", "themes", ["dataset_id"])

    op.create_table(
        "feedback_units",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "review_id", sa.Integer, sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("start_offset", sa.Integer, server_default="0"),
        sa.Column("end_offset", sa.Integer, server_default="0"),
        sa.Column("sentiment", sa.String(20)),
        sa.Column("sentiment_score", sa.Float),
        sa.Column("embedding", Vector(EMBEDDING_DIM)),
        sa.Column("theme_id", sa.Integer, sa.ForeignKey("themes.id", ondelete="SET NULL")),
        sa.Column("confidence", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_feedback_units_review_id", "feedback_units", ["review_id"])
    op.create_index("ix_feedback_units_theme_id", "feedback_units", ["theme_id"])
    op.execute(
        "CREATE INDEX ix_feedback_units_embedding_hnsw ON feedback_units "
        "USING hnsw (embedding vector_cosine_ops)"
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "dataset_id",
            sa.Integer,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "theme_id", sa.Integer, sa.ForeignKey("themes.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text),
        sa.Column("severity", sa.String(20), server_default="low"),
        sa.Column("impact_score", sa.Float, server_default="0.0"),
        sa.Column("first_detected_at", sa.DateTime(timezone=True)),
        sa.Column("last_detected_at", sa.DateTime(timezone=True)),
        sa.Column("growth_percent", sa.Float),
        sa.Column("likely_driver", sa.String(255)),
        sa.Column("root_cause_confidence", sa.Float),
        sa.Column("affected_platforms", sa.JSON),
        sa.Column("affected_versions", sa.JSON),
        sa.Column("affected_devices", sa.JSON),
        sa.Column("recommended_owner", sa.String(100)),
        sa.Column("recommended_priority", sa.String(10)),
        sa.Column("status", sa.String(20), server_default="open"),
        sa.Column("action_report", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_incidents_dataset_id", "incidents", ["dataset_id"])
    op.create_index("ix_incidents_theme_id", "incidents", ["theme_id"])

    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "incident_id",
            sa.Integer,
            sa.ForeignKey("incidents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("review_id", sa.Integer, sa.ForeignKey("reviews.id", ondelete="SET NULL")),
        sa.Column(
            "feedback_unit_id", sa.Integer, sa.ForeignKey("feedback_units.id", ondelete="SET NULL")
        ),
        sa.Column("evidence_type", sa.String(50), server_default="representative_review"),
        sa.Column("evidence_text", sa.Text, nullable=False),
        sa.Column("relevance_score", sa.Float),
    )
    op.create_index("ix_evidence_incident_id", "evidence", ["incident_id"])

    op.create_table(
        "human_feedback",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("theme_id", sa.Integer, sa.ForeignKey("themes.id", ondelete="CASCADE")),
        sa.Column(
            "feedback_unit_id", sa.Integer, sa.ForeignKey("feedback_units.id", ondelete="CASCADE")
        ),
        sa.Column("old_label", sa.String(255)),
        sa.Column("new_label", sa.String(255)),
        sa.Column("user_action", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_human_feedback_theme_id", "human_feedback", ["theme_id"])
    op.create_index("ix_human_feedback_feedback_unit_id", "human_feedback", ["feedback_unit_id"])


def downgrade() -> None:
    op.drop_table("human_feedback")
    op.drop_table("evidence")
    op.drop_table("incidents")
    op.drop_index("ix_feedback_units_embedding_hnsw", table_name="feedback_units")
    op.drop_table("feedback_units")
    op.drop_table("themes")
    op.drop_table("reviews")
    op.drop_table("datasets")
    op.drop_table("users")
