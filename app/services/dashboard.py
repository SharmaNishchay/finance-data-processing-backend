from datetime import date
from decimal import Decimal

from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RecordType
from app.models.financial_record import FinancialRecord
from app.schemas.dashboard import CategoryTotal, DashboardSummary, RecentActivity, TrendPoint


async def build_dashboard_summary(session: AsyncSession) -> DashboardSummary:
    totals_query = select(
        func.coalesce(
            func.sum(
                case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)
            ),
            0,
        ).label("income"),
        func.coalesce(
            func.sum(
                case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)
            ),
            0,
        ).label("expense"),
    )
    totals_result = await session.execute(totals_query)
    totals = totals_result.one()

    total_income: Decimal = totals.income
    total_expense: Decimal = totals.expense
    net_balance = total_income - total_expense

    category_query = (
        select(
            FinancialRecord.category,
            func.coalesce(func.sum(FinancialRecord.amount), 0).label("total"),
        )
        .group_by(FinancialRecord.category)
        .order_by(desc("total"))
    )
    category_result = await session.execute(category_query)
    category_wise_totals = [
        CategoryTotal(category=row.category, total=row.total) for row in category_result.all()
    ]

    recent_query = (
        select(FinancialRecord)
        .order_by(desc(FinancialRecord.record_date), desc(FinancialRecord.created_at))
        .limit(5)
    )
    recent_result = await session.execute(recent_query)
    recent_activity = [
        RecentActivity(
            id=record.id,
            category=record.category,
            amount=record.amount,
            type=record.type.value,
            record_date=record.record_date,
        )
        for record in recent_result.scalars().all()
    ]

    trends_query = (
        select(
            func.date_format(FinancialRecord.record_date, "%Y-%m-01").label("month_start"),
            func.coalesce(
                func.sum(
                    case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)
                ),
                0,
            ).label("income"),
            func.coalesce(
                func.sum(
                    case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)
                ),
                0,
            ).label("expense"),
        )
        .group_by("month_start")
        .order_by("month_start")
    )
    trends_result = await session.execute(trends_query)
    monthly_trends = [
        TrendPoint(period=date.fromisoformat(row.month_start), income=row.income, expense=row.expense)
        for row in trends_result.all()
    ]

    return DashboardSummary(
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        category_wise_totals=category_wise_totals,
        recent_activity=recent_activity,
        monthly_trends=monthly_trends,
    )
