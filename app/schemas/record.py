from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RecordType


class RecordCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    type: RecordType
    category: str = Field(min_length=2, max_length=120)
    record_date: date
    notes: str | None = Field(default=None, max_length=500)


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    type: RecordType | None = None
    category: str | None = Field(default=None, min_length=2, max_length=120)
    record_date: date | None = None
    notes: str | None = Field(default=None, max_length=500)


class RecordOut(BaseModel):
    id: int
    amount: Decimal
    type: RecordType
    category: str
    record_date: date
    notes: str | None
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
