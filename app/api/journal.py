from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
from app.models.account import Account
from app.schemas.journal_entry import JournalEntryCreate
from app.schemas.journal_read import JournalEntryRead
from app.schemas.journal_detail import JournalDetailRead
from app.services.journal_service import (
    create_journal_draft,
    post_journal_entry,
)

router = APIRouter(
    prefix="/journals",
    tags=["Journals"]
)

# ---------------------------------------------------------------------
# CREATE JOURNAL DRAFT
# ---------------------------------------------------------------------

@router.post("/draft")
async def create_draft(
    payload: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    entry = await create_journal_draft(db, payload)

    return {
        "id": entry.id,
        "journal_number": entry.journal_number,
        "status": "draft",
        "entry_date": entry.entry_date,
        "description": entry.description,
    }


# ---------------------------------------------------------------------
# POST JOURNAL (FINALIZE)
# ---------------------------------------------------------------------

@router.post("/{entry_id}/post")
async def post_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    entry = await post_journal_entry(db, entry_id)

    return {
        "id": entry.id,
        "journal_number": entry.journal_number,
        "status": "posted",
    }


# ---------------------------------------------------------------------
# LIST JOURNAL ENTRIES
# ---------------------------------------------------------------------

@router.get(
    "/",
    response_model=list[JournalEntryRead],
    summary="List journal entries",
)
async def list_journal_entries(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JournalEntry)
        .order_by(JournalEntry.created_at.desc())
    )
    return result.scalars().all()


# ---------------------------------------------------------------------
# JOURNAL DETAIL (READ-ONLY)
# ---------------------------------------------------------------------

@router.get(
    "/{entry_id}",
    response_model=JournalDetailRead,
    summary="Get journal entry detail",
)
async def get_journal_detail(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.id == entry_id)
        .options(selectinload(JournalEntry.lines))
    )

    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Journal not found")

    lines = []

    for line in entry.lines:
        acc = await db.get(Account, line.account_id)

        if not acc:
            raise HTTPException(
                status_code=500,
                detail="Journal line references missing account"
            )

        lines.append(
            {
                "account_code": acc.code,
                "debit": float(line.debit),
                "credit": float(line.credit),
            }
        )

    return {
        "id": entry.id,
        "journal_number": entry.journal_number,
        "entry_date": entry.entry_date,
        "description": entry.description,
        "is_posted": entry.is_posted,
        "lines": lines,
    }