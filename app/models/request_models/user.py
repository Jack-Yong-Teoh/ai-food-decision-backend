from pydantic import constr, field_validator
from app.models.pydantic_schemas.base import RequestModel
from app.services.authentication import generate_password_hash


class CreateUserRequestModel(RequestModel):
    username: str
    first_name: str
    last_name: str
    password: constr(min_length=8)  # type: ignore
    is_active: bool = True
    is_superuser: bool = False

    @field_validator("password")
    def validate_password(cls, value):
        return generate_password_hash(value)


class UpdateUserRequestModel(RequestModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class UpdateProfileRequestModel(RequestModel):
    first_name: str | None = None
    last_name: str | None = None


class UpdateUserPasswordRequestModel(RequestModel):
    password: constr(min_length=8)  # type: ignore

    @field_validator("password")
    def validate_password(cls, value):
        return generate_password_hash(value)
