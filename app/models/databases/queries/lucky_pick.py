from datetime import datetime
from app.models.databases.queries.base import QueryResultModel, LazyLoadResult


class DetailedLuckyPickResultModel(QueryResultModel):
    id: int | None = None
    option_name: str | None = None
    description: str | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None


class LazyloadLuckyPickQueryResultModel(QueryResultModel):
    id: int | None = None
    option_name: str | None = None
    description: str | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None


class LazyloadLuckyPickResultModel(LazyLoadResult):
    data: list[LazyloadLuckyPickQueryResultModel]
