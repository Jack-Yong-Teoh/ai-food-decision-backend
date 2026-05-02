from pydantic import constr, field_validator
from app.services.authentication import generate_password_hash
from app.models.pydantic_schemas.base import RequestModel


class LoginUserRequestModel(RequestModel):
    username: str
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        return generate_password_hash(value)


class SignUpRequestModel(RequestModel):
    username: str
    first_name: str
    last_name: str
    password: constr(min_length=8)  # type: ignore

    @field_validator("password")
    def validate_password(cls, value):
        return generate_password_hash(value)


class RefreshTokenRequestModel(RequestModel):
    refresh_token: str


class ChangePasswordRequestModel(RequestModel):
    current_password: str
    new_password: constr(min_length=8)  # type: ignore

    @field_validator("current_password")
    def validate_current_password(cls, value):
        return generate_password_hash(value)

    @field_validator("new_password")
    def validate_new_password(cls, value):
        return generate_password_hash(value)


class ResetPasswordRequestModel(RequestModel):
    password: constr(min_length=8)  # type: ignore

    @field_validator("password")
    def validate_password(cls, value):
        return generate_password_hash(value)
