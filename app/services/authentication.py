from typing import Optional
import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jose import jwt
from sqlalchemy.orm import Session
from redis import Redis
from fastapi import Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from app.models.databases.orm.user import User
from app.models.enums.authentication import JWTTokenScope
from app.models.exceptions import UnauthorizedException
from app.models.services.authentication import JWTTokenModel, LoginResult
from app.queries.user import get_user, save_user
from app.redis import redis as redis_app
from app.services.redis import (
    handle_login_success,
    handle_logout_success,
    invalidate_refreshed_session,
    key_exists,
)
from app.utilities.config import CONFIG
from app.utilities.contextvar import contextvar_session_user_id
from app.utilities.error_message import (
    account_deactivated,
    general_error,
    invalid_object,
    object_expired,
)

SECRET_KEY = CONFIG.AUTH.SECRET_KEY
ALGORITHM = "HS256"


TOKEN_AUTH_SCHEME = HTTPBearer()
API_KEY_AUTH_SCHEME = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def generate_password_hash(
    password: str,
):
    salt = CONFIG.AUTH.PASSWORD_SALT
    hash_password = hashlib.scrypt(
        password.encode(), salt=salt.encode(), n=16384, r=8, p=1
    ).hex()
    return hash_password


def create_token(
    user_id: int,
    scope: JWTTokenScope,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if not expires_delta:
        expires_delta = timedelta(hours=24)
    now = datetime.now(tz=ZoneInfo(CONFIG.OTHER.TIMEZONE))
    payload = JWTTokenModel(
        user_id=user_id,
        exp=now + expires_delta,
        iat=now,
        scope=scope.value,
    ).model_dump(exclude_none=True)
    token = jwt.encode(
        payload,
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return token


def create_access_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    return create_token(
        user_id=user_id,
        scope=JWTTokenScope.ACCESS_TOKEN,
        expires_delta=expires_delta,
    )


def create_refresh_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    expires_delta = timedelta(days=30) if expires_delta is None else expires_delta
    return create_token(
        user_id=user_id,
        scope=JWTTokenScope.REFRESH_TOKEN,
        expires_delta=expires_delta,
    )


def decode_token(
    token: str,
    raise_error: bool = True,
) -> Optional[JWTTokenModel]:
    try:
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return JWTTokenModel(**payload)

    except jwt.ExpiredSignatureError as e:
        if not raise_error:
            return None

        raise UnauthorizedException(
            object_expired(field_name="TOKEN"),
            extra={
                "token": token,
            },
        ) from e

    except jwt.JWTError as e:
        if not raise_error:
            return None

        raise UnauthorizedException(
            invalid_object(field_name="TOKEN"),
            extra={
                "token": token,
            },
        ) from e


def validate_token(
    redis: Redis,
    token: str,
    scope: JWTTokenScope,
) -> JWTTokenModel:
    token_exists = key_exists(
        redis=redis,
        key=token,
    )
    if not token_exists:
        raise UnauthorizedException(
            general_error("TOKEN INVALIDATED."),
            extra={
                "token": token,
                "scope": scope,
            },
        )

    payload = decode_token(token)
    if payload.scope != scope.value:
        raise UnauthorizedException(
            general_error("INVALID TOKEN SCOPE."),
            extra={
                "token": token,
                "scope": scope,
            },
        )
    return payload


def access_authorization(
    auth_creds: HTTPAuthorizationCredentials = Depends(TOKEN_AUTH_SCHEME),
) -> JWTTokenModel:
    access_token = auth_creds.credentials
    token_model = validate_token(
        redis=redis_app,
        token=access_token,
        scope=JWTTokenScope.ACCESS_TOKEN,
    )
    return token_model


def get_authorized_user_id(
    auth_creds: HTTPAuthorizationCredentials = Depends(TOKEN_AUTH_SCHEME),
) -> int:
    token_model = access_authorization(auth_creds)
    return token_model.user_id


def get_bearer_token(
    auth_creds: HTTPAuthorizationCredentials = Depends(TOKEN_AUTH_SCHEME),
) -> str:
    access_token = auth_creds.credentials
    return access_token


def handle_login_session(
    write_db: Session,
    redis: Redis,
    user: User,
    ip_address: str = None,
    access_token_expires_delta: Optional[timedelta] = None,
    refresh_token_expires_delta: Optional[timedelta] = None,
) -> LoginResult:
    contextvar_session_user_id.set(user.id)

    # Generate tokens
    generated_access_token = create_access_token(
        user_id=user.id,
        expires_delta=access_token_expires_delta,
    )
    generated_refresh_token = create_refresh_token(
        user_id=user.id,
        expires_delta=refresh_token_expires_delta,
    )

    # Save tokens to redis
    handle_login_success(
        redis=redis,
        user_id=user.id,
        access_token=generated_access_token,
        refresh_token=generated_refresh_token,
    )

    # Save last login information
    user.last_access = datetime.now()
    if ip_address is not None:
        user.last_ip_address = ip_address
    user = save_user(
        db=write_db,
        user=user,
    )

    return LoginResult(
        access_token=generated_access_token,
        refresh_token=generated_refresh_token,
    )


def handle_login(
    write_db: Session,
    redis: Redis,
    username: str,
    password: str,
    ip_address: str = None,
    access_token_expires_delta: Optional[timedelta] = None,
    refresh_token_expires_delta: Optional[timedelta] = None,
) -> LoginResult:
    db_user = get_user(
        db=write_db,
        username=username,
        password=password,
        optional=True,
    )
    if db_user is None:
        raise UnauthorizedException(
            invalid_object(field_name="USERNAME PASSWORD"),
            extra={
                "username": username,
                "password": password,
            },
        )
    if not db_user.is_active:
        raise UnauthorizedException(
            account_deactivated(),
            extra={
                "db_user": db_user,
            },
        )

    return handle_login_session(
        write_db=write_db,
        redis=redis,
        user=db_user,
        ip_address=ip_address,
        access_token_expires_delta=access_token_expires_delta,
        refresh_token_expires_delta=refresh_token_expires_delta,
    )


def handle_logout(
    write_db: Session,
    redis: Redis,
    user_id: int,
    access_token: str,
    ip_address: str = None,
) -> None:
    db_user = get_user(
        db=write_db,
        user_id=user_id,
    )

    handle_logout_success(
        redis=redis,
        user_id=db_user.id,
        access_token=access_token,
    )

    db_user.last_access = datetime.now()
    if ip_address is not None:
        db_user.last_ip_address = ip_address
    db_user = save_user(
        db=write_db,
        user=db_user,
    )


def handle_refresh_token(
    write_db: Session,
    redis: Redis,
    refresh_token: str = None,
    ip_address: str = None,
    access_token_expires_delta: Optional[timedelta] = None,
    refresh_token_expires_delta: Optional[timedelta] = None,
):
    token_model = validate_token(
        redis=redis,
        token=refresh_token,
        scope=JWTTokenScope.REFRESH_TOKEN,
    )
    db_user = get_user(
        db=write_db,
        user_id=token_model.user_id,
        optional=True,
    )
    if db_user is None:
        raise UnauthorizedException(
            invalid_object("USER"),
            extra={
                "refresh_token": refresh_token,
                "ip_address": ip_address,
            },
        )

    invalidate_refreshed_session(
        redis=redis,
        refresh_token=refresh_token,
    )

    if not db_user.is_active:
        raise UnauthorizedException(
            account_deactivated(),
            extra={
                "db_user": db_user,
            },
        )

    return handle_login_session(
        write_db=write_db,
        redis=redis,
        user=db_user,
        ip_address=ip_address,
        access_token_expires_delta=access_token_expires_delta,
        refresh_token_expires_delta=refresh_token_expires_delta,
    )


def handle_signup(
    write_db: Session,
    redis: Redis,
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    ip_address: str = None,
    access_token_expires_delta: Optional[timedelta] = None,
    refresh_token_expires_delta: Optional[timedelta] = None,
):
    """
    Handle user signup by creating a user, creating a wallet, and logging them in.
    """
    from app.services.user import create_user as create_user_service
    from app.models.databases.orm.user import User

    # Create the user (which will also create a wallet)
    new_user = User(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        is_superuser=False,
    )

    db_user = create_user_service(
        write_db=write_db,
        read_db=write_db,
        user=new_user,
        auto_commit=False,
    )

    # Get the wallet that was created
    from app.queries.wallet import get_wallet

    db_wallet = get_wallet(
        db=write_db,
        user_id=db_user.id,
    )

    # Create login session
    login_result = handle_login_session(
        write_db=write_db,
        redis=redis,
        user=db_user,
        ip_address=ip_address,
        access_token_expires_delta=access_token_expires_delta,
        refresh_token_expires_delta=refresh_token_expires_delta,
    )

    return {
        "user_id": db_user.id,
        "wallet_id": db_wallet.id,
        "access_token": login_result.access_token,
        "refresh_token": login_result.refresh_token,
    }
