from sqlalchemy import Date, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.session import Base
import sqlalchemy as sa


class AccountingPeriod(Base):
    __tablename__ = "accounting_periods"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sa.Column(String(100), nullable=False, unique=True)
    start_date = sa.Column(Date, nullable=False)
    end_date = sa.Column(Date, nullable=False)

    is_closed = sa.Column(Boolean, nullable=False, default=False)

    closed_at = sa.Column(DateTime)
    closed_by = sa.Column(String(100))

    created_at = sa.Column(DateTime, server_default=func.now())