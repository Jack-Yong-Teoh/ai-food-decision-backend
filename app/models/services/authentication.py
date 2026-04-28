from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict


class JWTTokenModel(BaseModel):
    user_id: int
    exp: datetime
    iat: datetime
    scope: str

    model_config = ConfigDict(extra="forbid")


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
