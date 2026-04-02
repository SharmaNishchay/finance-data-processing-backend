from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_db_session)) -> User:
    existing_user = await session.execute(select(User).where(User.email == payload.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(**payload.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get(
    "",
    response_model=list[UserOut],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def list_users(
    role: UserRole | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> list[User]:
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    result = await session.execute(query.order_by(User.id.desc()))
    return list(result.scalars().all())


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    for key, value in updates.items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user
