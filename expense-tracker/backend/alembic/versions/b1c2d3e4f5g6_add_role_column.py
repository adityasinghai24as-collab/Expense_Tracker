"""Add role column and drop features_enabled

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2026-07-12 18:46:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add role column
    op.add_column('users', sa.Column('role', sa.String(), server_default='user', nullable=False))
    
    # Drop features_enabled column
    op.drop_column('users', 'features_enabled')


def downgrade() -> None:
    # Add back features_enabled column
    op.add_column('users', sa.Column('features_enabled', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    
    # Drop role column
    op.drop_column('users', 'role')
