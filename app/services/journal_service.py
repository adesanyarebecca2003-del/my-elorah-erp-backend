import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.account import Account
from app.models.journal_entry import JournalEntry
from app.models.journal_line import JournalLine
from app.schemas.journal_entry import JournalEntryCreate
from app.services.period_guard import ensure_period_open


# ---------------------------------------------------------------------
# Period utilities (future-proofed)
# ---------------------------------------------------------------------

def is_period_open(entry_date) -> bool:
    """
    Placeholder for accounting period validation.
    Intentionally simple for now.
    """
    return True


def generate_journal_number() -> str:
    """
    Generates a human-readable journal reference.
    Safe for production (UUID-based, collision-resistant).
    """
    return f"JE-{uuid.uuid4().hex[:10].upper()}"


# ---------------------------------------------------------------------
# CORE SERVICE: CREATE JOURNAL DRAFT (LOCK 3 LIVES HERE)
# ---------------------------------------------------------------------

async def create_journal_draft(
    db: AsyncSession,
    payload: JournalEntryCreate
) -> JournalEntry:
    """
    Creates a fully validated, unposted (draft) journal entry.

    LOCKS ENFORCED:
    - Period must be open
    - Accounts must exist
    - Accounts must be active & posting
    - Journal must balance
    - Persistence is atomic
    """

    # ---- Period check (Lock 3: business rule)
    if not is_period_open(payload.entry_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accounting period is closed"
        )

    # ---- Resolve accounts
    account_codes = {line.account_code for line in payload.lines}

    result = await db.execute(
        select(Account).where(Account.code.in_(account_codes))
    )
    accounts = {acc.code: acc for acc in result.scalars().all()}

    if len(accounts) != len(account_codes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more account codes are invalid"
        )

    # ---- Validate journal lines & calculate totals
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

    for line in payload.lines:
        account = accounts[line.account_code]

        if not account.is_posting:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account {account.code} is not a posting account"
            )

        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account {account.code} is inactive"
            )

        total_debit += Decimal(str(line.debit))
        total_credit += Decimal(str(line.credit))

    # ---- Core accounting invariant (Lock 3)
    if total_debit != total_credit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Journal entry is not balanced"
        )

    # ---- Create journal entry (draft)
    entry = JournalEntry(
        journal_number=generate_journal_number(),
        entry_date=payload.entry_date,
        description=payload.description,
        is_posted=False
    )

    db.add(entry)
    await db.flush()  # ensures entry.id is available

    # ---- Secondary period guard (future accounting periods)
    await ensure_period_open(db, payload.entry_date)

    # ---- Create journal lines
    for line in payload.lines:
        account = accounts[line.account_code]
        db.add(
            JournalLine(
                entry_id=entry.id,
                account_id=account.id,
                debit=line.debit,
                credit=line.credit
            )
        )

    # ---- Commit atomically
    await db.commit()
    await db.refresh(entry)

    return entry


# ---------------------------------------------------------------------
# CORE SERVICE: POST JOURNAL (IMMUTABILITY GUARANTEE)
# ---------------------------------------------------------------------

async def post_journal_entry(
    db: AsyncSession,
    entry_id
) -> JournalEntry:
    """
    Posts a previously created draft journal entry.

    LOCKS ENFORCED:
    - Entry must exist
    - Entry must not already be posted
    - Posting is irreversible
    """

    result = await db.execute(
        select(JournalEntry).where(JournalEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )

    if entry.is_posted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Journal entry is already posted"
        )

    entry.is_posted = True

    await db.commit()
    await db.refresh(entry)

    return entry