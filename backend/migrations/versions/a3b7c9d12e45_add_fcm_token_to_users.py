"""Add fcm_token to users

Revision ID: a3b7c9d12e45
Revises: 1e3f16c582f3
Create Date: 2026-04-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3b7c9d12e45'
down_revision: Union[str, None] = '1e3f16c582f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('fcm_token', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'fcm_token')
