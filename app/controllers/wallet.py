from sqlalchemy.orm import Session
from fastapi import Depends
from app.models.request_models.wallet import (
    CreateWalletRequestModel,
)
from app.models.response_models.base import NoContentResponse
from app.models.response_models.wallet import (
    CreateWalletResponseModel,
    GetWalletResponseModel,
)
from app.models.databases.orm.wallet import Wallet
from app.models.databases.queries.wallet import DetailedWalletResultModel
from app.queries.wallet import (
    get_wallet as query_get_wallet,
)
from app.services.authentication import get_authorized_user_id
from app.services import wallet as wallet_services
from app.utilities.logger import logger
from app.utilities.postgresql import get_db, get_slave_db


def get_wallet(
    wallet_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_slave_db),
) -> GetWalletResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "wallet_id": wallet_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    db_wallet = query_get_wallet(
        db=db,
        wallet_id=wallet_id,
    )

    return db_wallet


def create_wallet(
    payload: CreateWalletRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
    slave_db: Session = Depends(get_slave_db),
) -> CreateWalletResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "authorized_user_id": authorized_user_id,
        },
    )
    db_wallet = wallet_services.create_wallet(
        write_db=db,
        read_db=slave_db,
        wallet=Wallet(**payload.model_dump()),
    )
    return db_wallet


def delete_wallet(
    wallet_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> NoContentResponse:
    logger.debug(
        "Payload Received",
        extra={
            "wallet_id": wallet_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    wallet_services.delete_wallet(
        write_db=db,
        wallet_id=wallet_id,
    )

    return NoContentResponse()


def get_wallet_by_user(
    user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_slave_db),
) -> GetWalletResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "user_id": user_id,
        },
    )

    db_wallet = wallet_services.get_wallet_by_user(
        read_db=db,
        user_id=user_id,
    )

    return db_wallet
