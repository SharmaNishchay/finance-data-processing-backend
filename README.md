# Finance Data Processing and Access Control Backend

FastAPI + MySQL backend implementing:
- User and role management (`viewer`, `analyst`, `admin`)
- Financial records CRUD
- Dashboard summary aggregations
- Role-based access control
- Validation and error handling

## Tech Stack
- FastAPI
- SQLAlchemy (async)
- MySQL (`aiomysql` driver)
- Pydantic v2

## Run Locally

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment file:

```bash
cp .env.example .env
```

4. Create MySQL database:

```sql
CREATE DATABASE finance_backend;
```

5. Start server:

```bash
uvicorn app.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`.

## Authentication and Access Control (Mock)

This project uses a simple mock auth approach for assignment purposes:
- Pass `X-User-Id` header in every protected request.
- The backend loads the user and enforces role + active status checks.

If header is missing/invalid/inactive, request is rejected.

On startup, the app auto-creates one default admin user (if not already present):
- name: from `DEFAULT_ADMIN_NAME`
- email: from `DEFAULT_ADMIN_EMAIL`

Use this user first, then create other users from the admin APIs.

## Roles
- **viewer**: dashboard summary only
- **analyst**: read records + dashboard summary access
- **admin**: full access (manage users and records)

## API Overview

### Health
- `GET /health`

### Users (Admin only)
- `POST /users` create user
- `GET /users` list users (optional role filter)
- `PATCH /users/{user_id}` update role/status/name

### Financial Records
- `POST /records` (admin)
- `GET /records` (analyst/admin)
  - Filters: `record_type`, `category`, `start_date`, `end_date`
  - Pagination: `page`, `page_size`
- `PATCH /records/{record_id}` (admin)
- `DELETE /records/{record_id}` (admin)

### Dashboard
- `GET /dashboard/summary` (viewer/analyst/admin)
  - total income
  - total expenses
  - net balance
  - category-wise totals
  - recent activity
  - monthly trends

## Data Model

### `users`
- `id`
- `name`
- `email` (unique)
- `role` (`viewer|analyst|admin`)
- `status` (`active|inactive`)
- `created_at`, `updated_at`

### `financial_records`
- `id`
- `amount`
- `type` (`income|expense`)
- `category`
- `record_date`
- `notes`
- `created_by_user_id` (FK -> users.id)
- `created_at`, `updated_at`

## Validation and Error Handling
- Strong Pydantic input validation
- 400 for invalid updates/filters
- 401 for missing/invalid user header
- 403 for inactive users or insufficient role
- 404 for missing records/users

## Assumptions
- Simple mock auth via `X-User-Id` is sufficient for this assignment.
- DB schema is auto-created at startup using SQLAlchemy metadata.
- A default admin bootstrap user is auto-created at startup.
- Currency precision stored as `NUMERIC(12,2)`.
