from typing import Optional
from pydantic import BaseModel, ConfigDict


class AccessTokenModel(BaseModel):
    user_id: int
    refresh_token: Optional[str]

    model_config = ConfigDict(
        extra="forbid",
    )


class RefreshTokenModel(BaseModel):
    user_id: int
    access_token: str

    model_config = ConfigDict(
        extra="forbid",
    )


class UserTokenModel(BaseModel):
    access_token: str
    refresh_token: Optional[str]

    model_config = ConfigDict(
        extra="forbid",
    )


class ClientInfoModel(BaseModel):
    password: Optional[str]

    model_config = ConfigDict(
        extra="forbid",
    )
