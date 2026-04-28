from sqlalchemy.orm import Session
from fastapi import Depends
from app.models.request_models.authentication import (
    RefreshTokenRequestModel,
    LoginUserRequestModel,
    ChangePasswordRequestModel,
)
from app.models.response_models.authentication import (
    LoginResponseModel,
    LogoutResponseModel,
    ChangePasswordResponseModel,
)
from app.redis import redis
from app.services.authentication import (
    handle_login,
    get_authorized_user_id,
    get_bearer_token,
    handle_logout,
    handle_refresh_token,
)
from app.services.user import update_password
from app.utilities.logger import logger
from app.utilities.request import get_ip_address
from app.utilities.postgresql import get_db, get_slave_db


def login(
    payload: LoginUserRequestModel,
    ip_address: str = Depends(get_ip_address),
    db: Session = Depends(get_db),
) -> LoginResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "ip_address": ip_address,
        },
    )

    result = handle_login(
        write_db=db,
        redis=redis,
        ip_address=ip_address,
        **payload.model_dump(),
    )

    return LoginResponseModel(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


def logout(
    user_id: int = Depends(get_authorized_user_id),
    access_token: str = Depends(get_bearer_token),
    ip_address: str = Depends(get_ip_address),
    db: Session = Depends(get_db),
) -> LogoutResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "user_id": user_id,
            "access_token": access_token,
            "ip_address": ip_address,
        },
    )

    handle_logout(
        write_db=db,
        redis=redis,
        user_id=user_id,
        access_token=access_token,
        ip_address=ip_address,
    )

    return LogoutResponseModel(result="success")


def refresh_token(
    payload: RefreshTokenRequestModel,
    ip_address: str = Depends(get_ip_address),
    db: Session = Depends(get_db),
) -> LoginResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "ip_address": ip_address,
        },
    )

    result = handle_refresh_token(
        write_db=db,
        redis=redis,
        ip_address=ip_address,
        **payload.model_dump(),
    )

    return LoginResponseModel(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


def change_password(
    payload: ChangePasswordRequestModel,
    user_id: int = Depends(get_authorized_user_id),
    ip_address: str = Depends(get_ip_address),
    db: Session = Depends(get_db),
    slave_db: Session = Depends(get_slave_db),
) -> ChangePasswordResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "user_id": user_id,
            "ip_address": ip_address,
        },
    )

    update_password(
        write_db=db,
        read_db=slave_db,
        user_id=user_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )

    return ChangePasswordResponseModel(id=user_id)
