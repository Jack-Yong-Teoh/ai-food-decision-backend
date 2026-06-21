from datetime import datetime
from app.models.databases.queries.base import QueryResultModel


class DetailedWalletResultModel(QueryResultModel):
    id: int | None = None
    balance: float | None = None
    user_id: int | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None
