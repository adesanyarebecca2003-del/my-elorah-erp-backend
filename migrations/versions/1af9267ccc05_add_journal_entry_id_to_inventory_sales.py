"""add journal_entry_id to inventory_sales

Revision ID: 1af9267ccc05
Revises: 247c84529b7a
Create Date: 2026-02-12 16:34:19.505404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1af9267ccc05'
down_revision: Union[str, Sequence[str], None] = '247c84529b7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "inventory_sales",
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_inventory_sales_journal_entry_id",
        "inventory_sales",
        "journal_entries",
        ["journal_entry_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "fk_inventory_sales_journal_entry_id",
        "inventory_sales",
        type_="foreignkey",
    )
    op.drop_column("inventory_sales", "journal_entry_id")
