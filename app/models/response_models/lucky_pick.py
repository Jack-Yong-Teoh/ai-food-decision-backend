from app.models.pydantic_schemas.base import ResponseModel


class CreateLuckyPickResponseModel(ResponseModel):
    id: int


class UpdateLuckyPickResponseModel(ResponseModel):
    id: int