from app.models.pydantic_schemas.base import ResponseModel


class CreateTransactionResponseModel(ResponseModel):
    id: int
