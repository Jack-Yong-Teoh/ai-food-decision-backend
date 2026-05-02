from app.models.pydantic_schemas.base import RequestModel


class CreateLuckyPickRequestModel(RequestModel):
    option_name: str
    description: str


class UpdateLuckyPickRequestModel(RequestModel):
    option_name: str | None = None
    description: str | None = None
