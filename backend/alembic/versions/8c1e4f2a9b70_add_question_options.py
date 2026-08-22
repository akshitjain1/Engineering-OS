"""add question options and attempt fields

Revision ID: 8c1e4f2a9b70
Revises: dd0d6237bbc3
Create Date: 2026-08-18 22:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c1e4f2a9b70"
down_revision: Union[str, Sequence[str], None] = "dd0d6237bbc3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("lesson_questions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("options", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("last_answer", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("last_correct", sa.Boolean(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("lesson_questions", schema=None) as batch_op:
        batch_op.drop_column("last_correct")
        batch_op.drop_column("attempt_count")
        batch_op.drop_column("last_answer")
        batch_op.drop_column("options")
