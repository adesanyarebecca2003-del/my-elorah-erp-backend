"""add password hash to users

Revision ID: 05619782e1f3
Revises: b2a089bf35d1
Create Date: 2026-02-07 23:29:47.752013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05619782e1f3'
down_revision: Union[str, Sequence[str], None] = 'b2a089bf35d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
