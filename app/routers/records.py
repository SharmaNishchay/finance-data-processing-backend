from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import get_current_user, require_roles
from app.models.enums import RecordType, UserRole
from app.models.financial_record import FinancialRecord
from app.models.user import User
from app.schemas.record import RecordCreate, RecordOut, RecordUpdate

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post(
    "",
    response_model=RecordOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def create_record(
    payload: RecordCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> FinancialRecord:
    record = FinancialRecord(**payload.model_dump(), created_by_user_id=current_user.id)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


@router.get(
    "",
    response_model=list[RecordOut],
    dependencies=[Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))],
)
async def list_records(
    record_type: RecordType | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> list[FinancialRecord]:
    query = select(FinancialRecord)

    if record_type is not None:
        query = query.where(FinancialRecord.type == record_type)
    if category:
        query = query.where(FinancialRecord.category == category)
    if start_date:
        query = query.where(FinancialRecord.record_date >= start_date)
    if end_date:
        query = query.where(FinancialRecord.record_date <= end_date)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before or equal to end_date")

    query = query.order_by(FinancialRecord.record_date.desc(), FinancialRecord.id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await session.execute(query)
    return list(result.scalars().all())


@router.patch(
    "/{record_id}",
    response_model=RecordOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def update_record(
    record_id: int,
    payload: RecordUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> FinancialRecord:
    result = await session.execute(select(FinancialRecord).where(FinancialRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    for key, value in updates.items():
        setattr(record, key, value)

    await session.commit()
    await session.refresh(record)
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def delete_record(record_id: int, session: AsyncSession = Depends(get_db_session)) -> None:
    result = await session.execute(select(FinancialRecord).where(FinancialRecord.id == record_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    await session.delete(record)
    await session.commit()
