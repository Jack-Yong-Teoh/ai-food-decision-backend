from datetime import datetime

from app.models.databases.queries.base import QueryResultModel, LazyLoadResult
from app.models.enums.transaction import TransactionType


class DetailedTransactionResultModel(QueryResultModel):
    id: int | None = None
    wallet_id: int | None = None
    amount: float | None = None
    transaction_type: TransactionType | None = None
    reference_id: str | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None


class LazyloadTransactionQueryResultModel(QueryResultModel):
    id: int | None = None
    wallet_id: int | None = None
    amount: float | None = None
    transaction_type: TransactionType | None = None
    reference_id: str | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None


class LazyloadTransactionResultModel(LazyLoadResult):
    data: list[LazyloadTransactionQueryResultModel]
