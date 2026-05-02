from sqlalchemy.orm import Session
from app.models.databases.orm.wallet import Wallet
from app.models.exceptions.not_found_exception import NotFoundException
from app.queries.wallet import get_wallet, save_wallet
from app.utilities.logger import logger


def create_wallet(
    write_db: Session,
    read_db: Session,
    wallet: Wallet,
    auto_commit: bool = True,
) -> Wallet:
    db_wallet = save_wallet(db=write_db, wallet=wallet, auto_commit=False)

    logger.debug(
        "Wallet Created",
        extra={
            "db_wallet": db_wallet,
        },
    )

    if auto_commit:
        write_db.commit()
        write_db.refresh(db_wallet)

    return db_wallet


def get_wallet_by_user(
    read_db: Session,
    user_id: int,
) -> Wallet:
    db_wallet = get_wallet(
        db=read_db,
        user_id=user_id,
        optional=False,
    )
    return db_wallet


def delete_wallet(
    write_db: Session,
    wallet_id: int,
    auto_commit: bool = True,
) -> None:
    db_wallet = get_wallet(
        db=write_db,
        wallet_id=wallet_id,
    )

    write_db.delete(db_wallet)

    if auto_commit:
        write_db.commit()

    logger.debug(
        "Wallet Deleted",
        extra={
            "db_wallet": db_wallet,
        },
    )
