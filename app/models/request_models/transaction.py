from app.models.pydantic_schemas.base import RequestModel
from app.models.enums.transaction import TransactionType


class CreateTransactionRequestModel(RequestModel):
    wallet_id: int
    amount: float
    transaction_type: TransactionType
    reference_id: str | None = None
