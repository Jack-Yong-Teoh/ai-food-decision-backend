from app.models.pydantic_schemas.base import ResponseModel


class CreateWalletResponseModel(ResponseModel):
    id: int
class GetWalletResponseModel(ResponseModel):
    id: int
    balance: float
    user_id: int

