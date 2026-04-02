from enum import StrEnum


class UserRole(StrEnum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class RecordType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
