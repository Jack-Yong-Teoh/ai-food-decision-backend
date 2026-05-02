from typing import Optional
from sqlalchemy import BinaryExpression, ColumnOperators
from sqlalchemy.orm import Session
from app.models.databases.orm.wallet import Wallet
from app.models.databases.queries.wallet import DetailedWalletResultModel
from app.models.exceptions.not_found_exception import NotFoundException


def get_filter_criterion(
    wallet_id: int = None,
    user_id: int = None,
    get_one: bool = True,
) -> list[BinaryExpression]:
    criterion = [
        (None if wallet_id is None else ColumnOperators.__eq__(Wallet.id, wallet_id)),
        (None if user_id is None else ColumnOperators.__eq__(Wallet.user_id, user_id)),
    ]
    criterion = [x for x in criterion if x is not None]
    if get_one and len(criterion) == 0:
        raise ValueError("No filtering criteria provided")
    return criterion


def get_wallets(
    db: Session,
    wallet_id: int = None,
    user_id: int = None,
) -> list[Wallet]:
    criterion = get_filter_criterion(
        wallet_id=wallet_id,
        user_id=user_id,
        get_one=False,
    )
    db_wallets = db.query(Wallet).filter(*criterion).all()
    return db_wallets


def get_wallet(
    db: Session,
    wallet_id: int = None,
    user_id: int = None,
    optional: bool = False,
) -> Optional[Wallet]:
    criterion = get_filter_criterion(
        wallet_id=wallet_id,
        user_id=user_id,
    )
    db_wallet = db.query(Wallet).filter(*criterion).one_or_none()
    if db_wallet is None and not optional:
        raise NotFoundException(
            "WALLET_NOT_FOUND",
            extra={
                "wallet_id": wallet_id,
                "user_id": user_id,
            },
        )
    return db_wallet


def save_wallet(
    db: Session,
    wallet: Wallet,
    auto_commit: bool = True,
) -> Wallet:
    db.add(wallet)
    # pylint: disable-next=expression-not-assigned
    db.commit() if auto_commit else db.flush()
    db.refresh(wallet)
    return wallet
