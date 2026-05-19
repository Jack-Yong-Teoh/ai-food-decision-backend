from app.models.pydantic_schemas.base import ResponseModel


class LoginResponseModel(ResponseModel):
    access_token: str
    refresh_token: str


class SignUpResponseModel(ResponseModel):
    id: int
    wallet_id: int


class LogoutResponseModel(ResponseModel):
    result: str


class ChangePasswordResponseModel(ResponseModel):
    id: int
