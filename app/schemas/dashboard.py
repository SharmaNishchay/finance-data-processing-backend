from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class TrendPoint(BaseModel):
    period: date
    income: Decimal
    expense: Decimal


class RecentActivity(BaseModel):
    id: int
    category: str
    amount: Decimal
    type: str
    record_date: date


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    category_wise_totals: list[CategoryTotal]
    recent_activity: list[RecentActivity]
    monthly_trends: list[TrendPoint]
