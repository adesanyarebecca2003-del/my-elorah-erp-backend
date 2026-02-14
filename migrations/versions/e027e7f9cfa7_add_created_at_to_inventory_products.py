"""add created_at to inventory_products

Revision ID: e027e7f9cfa7
Revises: fbaa20b8e9d7
Create Date: 2026-02-09 10:46:28.937525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e027e7f9cfa7'
down_revision: Union[str, Sequence[str], None] = 'fbaa20b8e9d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "inventory_products",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("inventory_products", "created_at")