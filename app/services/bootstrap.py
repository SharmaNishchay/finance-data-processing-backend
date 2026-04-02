from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.enums import UserRole, UserStatus
from app.models.user import User


async def ensure_default_admin(session: AsyncSession) -> None:
    result = await session.execute(
        select(User).where(User.email == settings.default_admin_email)
    )
    admin = result.scalar_one_or_none()
    if admin is not None:
        return

    session.add(
        User(
            name=settings.default_admin_name,
            email=settings.default_admin_email,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
    )
    await session.commit()
