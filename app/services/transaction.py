from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.databases.orm.transaction import Transaction
from app.models.enums.transaction import TransactionType
from app.models.exceptions.conflict_exception import ConflictException
from app.queries.transaction import get_transaction, save_transaction
from app.queries.user import get_user
from app.queries.wallet import get_wallet, save_wallet
from app.models.exceptions.forbidden_exception import ForbiddenException
from app.utilities.error_message import general_error
from app.utilities.logger import logger


def _get_wallet_balance_delta(transaction: Transaction) -> Decimal:
    transaction_amount = Decimal(str(transaction.amount))
    transaction_type = TransactionType(transaction.transaction_type)

    if transaction_type in [
        TransactionType.PAYMENT,
        TransactionType.DEDUCT,
    ]:
        return -transaction_amount

    if transaction_type in [
        TransactionType.TOP_UP,
        TransactionType.REFUND,
    ]:
        return transaction_amount

    raise ValueError(f"Unsupported transaction type: {transaction.transaction_type}")


def create_transaction(
    write_db: Session,
    transaction: Transaction,
    authorized_user_id: int,
    auto_commit: bool = True,
) -> Transaction:
    db_user = get_user(db=write_db, user_id=authorized_user_id)

    if not db_user.is_superuser and db_user.wallet_id != transaction.wallet_id:
        raise ForbiddenException(
            general_error("WALLET NOT OWNED BY USER"),
            extra={
                "user_id": authorized_user_id,
                "user_wallet_id": db_user.wallet_id,
                "transaction_wallet_id": transaction.wallet_id,
            },
        )

    if (
        TransactionType(transaction.transaction_type)
        in [
            TransactionType.REFUND,
            TransactionType.DEDUCT,
        ]
        and not db_user.is_superuser
    ):
        raise ForbiddenException(
            general_error("USER NOT ALLOWED"),
            extra={
                "user_id": authorized_user_id,
                "transaction_type": transaction.transaction_type,
            },
        )

    db_wallet = get_wallet(
        db=write_db,
        wallet_id=transaction.wallet_id,
    )
    wallet_balance_delta = _get_wallet_balance_delta(transaction)
    updated_balance = Decimal(str(db_wallet.balance)) + wallet_balance_delta

    if updated_balance < 0:
        raise ConflictException(
            general_error("INSUFFICIENT WALLET BALANCE"),
            extra={
                "wallet_id": transaction.wallet_id,
                "wallet_balance": db_wallet.balance,
                "transaction_amount": transaction.amount,
                "transaction_type": transaction.transaction_type,
            },
        )

    db_wallet.balance = updated_balance
    save_wallet(
        db=write_db,
        wallet=db_wallet,
        auto_commit=False,
    )

    db_transaction = save_transaction(
        db=write_db,
        transaction=transaction,
        auto_commit=False,
    )

    logger.debug(
        "Transaction Created",
        extra={
            "db_transaction": db_transaction,
        },
    )

    if auto_commit:
        write_db.commit()
        write_db.refresh(db_transaction)

    return db_transaction


def get_transaction_by_id(
    read_db: Session,
    transaction_id: int,
) -> Transaction:
    db_transaction = get_transaction(
        db=read_db,
        transaction_id=transaction_id,
        optional=False,
    )
    return db_transaction
