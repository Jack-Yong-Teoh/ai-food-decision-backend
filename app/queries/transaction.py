from typing import Optional

from sqlalchemy import BinaryExpression, ColumnOperators, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from app.models.databases.orm.transaction import Transaction
from app.models.databases.queries.base import FilterModel, PaginateModel, SortModel
from app.models.databases.queries.transaction import LazyloadTransactionResultModel
from app.models.enums.transaction import TransactionType
from app.models.exceptions.not_found_exception import NotFoundException
from app.queries.base import lazyload_data


def get_filter_criterion(
    transaction_id: int = None,
    wallet_id: int = None,
    transaction_type: TransactionType = None,
    reference_id: str = None,
    get_one: bool = True,
) -> list[BinaryExpression]:
    criterion = [
        (
            None
            if transaction_id is None
            else ColumnOperators.__eq__(Transaction.id, transaction_id)
        ),
        (
            None
            if wallet_id is None
            else ColumnOperators.__eq__(Transaction.wallet_id, wallet_id)
        ),
        (
            None
            if transaction_type is None
            else ColumnOperators.__eq__(Transaction.transaction_type, transaction_type)
        ),
        (
            None
            if reference_id is None
            else ColumnOperators.__eq__(
                func.lower(Transaction.reference_id), func.lower(reference_id)
            )
        ),
    ]
    criterion = [x for x in criterion if x is not None]
    if get_one and len(criterion) == 0:
        raise ValueError("No filtering criteria provided")
    return criterion


def get_transactions(
    db: Session,
    transaction_id: int = None,
    wallet_id: int = None,
    transaction_type: TransactionType = None,
    reference_id: str = None,
) -> list[Transaction]:
    criterion = get_filter_criterion(
        transaction_id=transaction_id,
        wallet_id=wallet_id,
        transaction_type=transaction_type,
        reference_id=reference_id,
        get_one=False,
    )
    db_transactions = db.query(Transaction).filter(*criterion).all()
    return db_transactions


def get_transaction(
    db: Session,
    transaction_id: int = None,
    wallet_id: int = None,
    transaction_type: TransactionType = None,
    reference_id: str = None,
    optional: bool = False,
) -> Optional[Transaction]:
    criterion = get_filter_criterion(
        transaction_id=transaction_id,
        wallet_id=wallet_id,
        transaction_type=transaction_type,
        reference_id=reference_id,
    )
    db_transaction = db.query(Transaction).filter(*criterion).one_or_none()
    if db_transaction is None and not optional:
        raise NotFoundException(
            "TRANSACTION_NOT_FOUND",
            extra={
                "transaction_id": transaction_id,
                "wallet_id": wallet_id,
                "transaction_type": transaction_type,
                "reference_id": reference_id,
            },
        )
    return db_transaction


def save_transaction(
    db: Session,
    transaction: Transaction,
    auto_commit: bool = True,
) -> Transaction:
    db.add(transaction)
    # pylint: disable-next=expression-not-assigned
    db.commit() if auto_commit else db.flush()
    db.refresh(transaction)
    return transaction


async def lazyload_transactions(
    async_db: AsyncSession,
    filters: list[FilterModel],
    pagination: PaginateModel,
    sort: SortModel,
    search: str = None,
    included_fields: list[str] = None,
    excluded_fields: list[str] = None,
    export: bool = False,
) -> LazyloadTransactionResultModel:
    select_query = select(
        Transaction.id,
        Transaction.wallet_id,
        Transaction.amount,
        Transaction.transaction_type,
        Transaction.reference_id,
        Transaction.created_date,
        Transaction.modified_date,
    ).select_from(Transaction)
    results = await lazyload_data(
        async_db=async_db,
        select_query=select_query,
        filters=filters,
        pagination=pagination,
        sort=sort,
        search=search,
        included_fields=included_fields,
        excluded_fields=excluded_fields,
        export=export,
    )
    return LazyloadTransactionResultModel(**results.__dict__)
