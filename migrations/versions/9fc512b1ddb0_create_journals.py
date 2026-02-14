"""create journals

Revision ID: 9fc512b1ddb0
Revises: 872998ef7d19
Create Date: 2026-02-07 14:35:23.108052
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9fc512b1ddb0"
down_revision: Union[str, Sequence[str], None] = "872998ef7d19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "journal_entries",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("journal_number", sa.String(30), nullable=False, unique=True),
        sa.Column("entry_date", sa.Date, nullable=False, index=True),
        sa.Column("description", sa.String(255)),
        sa.Column("is_posted", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "journal_lines",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "entry_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("journal_entries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
            nullable=False,
        ),
        sa.Column("debit", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("credit", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_table("journal_lines")
    op.drop_table("journal_entries")