"""add curriculum slugs and resource provider

Revision ID: a4c91e2b7d11
Revises: 8c1e4f2a9b70
Create Date: 2026-08-18 22:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4c91e2b7d11"
down_revision: Union[str, Sequence[str], None] = "8c1e4f2a9b70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    "curriculum_tracks",
    "curriculum_levels",
    "curriculum_subjects",
    "curriculum_modules",
    "curriculum_topics",
    "curriculum_lessons",
    "curriculum_resources",
    "lesson_questions",
    "lesson_exercises",
]


def upgrade() -> None:
    for table in TABLES:
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.add_column(sa.Column("slug", sa.String(length=160), nullable=True))
            batch_op.create_index(batch_op.f(f"ix_{table}_slug"), ["slug"], unique=True)
    with op.batch_alter_table("curriculum_resources", schema=None) as batch_op:
        batch_op.add_column(sa.Column("provider", sa.String(length=100), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("curriculum_resources", schema=None) as batch_op:
        batch_op.drop_column("provider")
    for table in reversed(TABLES):
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.drop_index(batch_op.f(f"ix_{table}_slug"))
            batch_op.drop_column("slug")
