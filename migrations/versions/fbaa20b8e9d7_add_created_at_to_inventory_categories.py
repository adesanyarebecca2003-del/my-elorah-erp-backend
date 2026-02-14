"""add created_at to inventory_categories

Revision ID: fbaa20b8e9d7
Revises: 05619782e1f3
Create Date: 2026-02-08 19:57:53.742366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbaa20b8e9d7'
down_revision: Union[str, Sequence[str], None] = '05619782e1f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'inventory_categories',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        )
    )


def downgrade():
    op.drop_column('inventory_categories', 'created_at')
