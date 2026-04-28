from enum import Enum


class JWTTokenScope(str, Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
