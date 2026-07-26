"""add icon to category

Revision ID: a1b2c3d4e5f6
Revises: fdda9f85c2eb
Create Date: 2026-07-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fdda9f85c2eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('icon', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('categories', 'icon')
