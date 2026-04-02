from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import build_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    dependencies=[Depends(require_roles(UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN))],
)
async def get_dashboard_summary(session: AsyncSession = Depends(get_db_session)) -> DashboardSummary:
    return await build_dashboard_summary(session)
