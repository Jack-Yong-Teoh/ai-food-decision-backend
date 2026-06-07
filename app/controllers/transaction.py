from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.decorators.export import export_async

from app.models.databases.orm.transaction import Transaction
from app.models.databases.queries.transaction import (
    DetailedTransactionResultModel,
    LazyloadTransactionResultModel,
)
from app.models.pydantic_schemas.base import LazyloadRequestModel
from app.models.request_models.transaction import CreateTransactionRequestModel
from app.models.response_models.transaction import CreateTransactionResponseModel
from app.queries.transaction import (
    get_transaction as query_get_transaction,
    lazyload_transactions as query_lazyload_transactions,
)
from app.services.authentication import get_authorized_user_id
from app.services import transaction as transaction_services
from app.utilities.logger import logger
from app.utilities.postgresql import get_db, get_slave_db, get_async_slave_db


def get_transaction(
    transaction_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_slave_db),
) -> DetailedTransactionResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "transaction_id": transaction_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    db_transaction = query_get_transaction(
        db=db,
        transaction_id=transaction_id,
    )

    return db_transaction


def create_transaction(
    payload: CreateTransactionRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> CreateTransactionResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "authorized_user_id": authorized_user_id,
        },
    )
    db_transaction = transaction_services.create_transaction(
        write_db=db,
        transaction=Transaction(**payload.model_dump()),
        authorized_user_id=authorized_user_id,
    )
    return db_transaction


@export_async
async def lazyload_transactions(
    payload: LazyloadRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    async_slave_db: AsyncSession = Depends(get_async_slave_db),
) -> LazyloadTransactionResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "authorized_user_id": authorized_user_id,
        },
    )

    return await query_lazyload_transactions(
        async_db=async_slave_db,
        filters=payload.filters,
        search=payload.search,
        pagination=payload.pagination,
        sort=payload.sort,
        included_fields=payload.included_fields,
        excluded_fields=payload.excluded_fields,
        export=payload.export,
    )
