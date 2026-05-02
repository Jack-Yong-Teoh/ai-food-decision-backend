from pydantic import Field
from app.models.pydantic_schemas.base import RequestModel


class CreateWalletRequestModel(RequestModel):
    balance: float = Field(default=0.0, ge=0)
    user_id: int

