from datetime import datetime
from app.models.databases.queries.base import QueryResultModel, LazyLoadResult


class DetailedUserResultModel(QueryResultModel):
    id: int | None = None
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    wallet_id: int | None = None
    last_access: datetime | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None


class LazyloadUserQueryResultModel(QueryResultModel):
    id: int | None = None
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    wallet_id: int | None = None
    last_access: datetime | None = None
    created_date: datetime | None = None


class LazyloadUserResultModel(LazyLoadResult):
    data: list[LazyloadUserQueryResultModel]
