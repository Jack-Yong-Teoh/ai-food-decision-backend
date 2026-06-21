from app.models.pydantic_schemas.base import ResponseModel


class CreateUserResponseModel(ResponseModel):
    id: int


class UpdateUserResponseModel(ResponseModel):
    id: int


class UpdateProfileResponseModel(ResponseModel):
    id: int


class UpdateUserPasswordResponseModel(ResponseModel):
    id: int
