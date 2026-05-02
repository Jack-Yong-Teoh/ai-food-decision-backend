from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.decorators.export import export_async
from app.models.pydantic_schemas.base import LazyloadRequestModel
from app.models.request_models.user import (
    UpdateUserRequestModel,
    CreateUserRequestModel,
    UpdateProfileRequestModel,
    UpdateUserPasswordRequestModel,
)
from app.models.response_models.base import NoContentResponse
from app.models.response_models.user import (
    UpdateUserResponseModel,
    CreateUserResponseModel,
    UpdateProfileResponseModel,
    UpdateUserPasswordResponseModel,
)
from app.models.databases.orm.user import User
from app.models.databases.queries.user import (
    DetailedUserResultModel,
    LazyloadUserResultModel,
)
from app.queries.user import (
    get_user as query_get_user,
    lazyload_users as query_lazyload_users,
)
from app.services.authentication import get_authorized_user_id
from app.services import user as user_services
from app.utilities.logger import logger
from app.utilities.postgresql import get_db, get_slave_db, get_async_slave_db


def get_user(
    user_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_slave_db),
) -> DetailedUserResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "user_id": user_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    db_user = query_get_user(
        db=db,
        user_id=user_id,
    )

    return db_user


def create_user(
    payload: CreateUserRequestModel,
    user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
    slave_db: Session = Depends(get_slave_db),
) -> CreateUserResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "user_id": user_id,
        },
    )
    db_user = user_services.create_user(
        write_db=db,
        read_db=slave_db,
        user=User(**payload.model_dump()),
    )
    return db_user


def update_user(
    user_id: int,
    payload: UpdateUserRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
    slave_db: Session = Depends(get_slave_db),
) -> UpdateUserResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(exclude_none=True),
            "user_id": user_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    db_user = user_services.update_user(
        write_db=db,
        read_db=slave_db,
        user_id=user_id,
        payload=payload.model_dump(exclude_none=True),
    )

    return UpdateUserResponseModel(id=db_user.id)


def delete_user(
    user_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> NoContentResponse:
    logger.debug(
        "Payload Received",
        extra={
            "user_id": user_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    user_services.delete_user(
        write_db=db,
        user_id=user_id,
    )

    return NoContentResponse()


@export_async
async def lazyload_users(
    payload: LazyloadRequestModel,
    user_id: int = Depends(get_authorized_user_id),
    async_slave_db: AsyncSession = Depends(get_async_slave_db),
) -> LazyloadUserResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "user_id": user_id,
        },
    )

    return await query_lazyload_users(
        async_db=async_slave_db,
        filters=payload.filters,
        search=payload.search,
        pagination=payload.pagination,
        sort=payload.sort,
        included_fields=payload.included_fields,
        excluded_fields=payload.excluded_fields,
        export=payload.export,
    )


def get_profile(
    user_id: int = Depends(get_authorized_user_id),
    slave_db: Session = Depends(get_slave_db),
) -> DetailedUserResultModel:
    logger.debug(
        "Payload Received",
        extra={"user_id": user_id},
    )
    return query_get_user(
        db=slave_db,
        user_id=user_id,
    )


def update_profile(
    payload: UpdateProfileRequestModel,
    user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
    slave_db: Session = Depends(get_slave_db),
) -> UpdateProfileResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "user_id": user_id,
        },
    )
    db_user = user_services.update_user(
        write_db=db,
        read_db=slave_db,
        user_id=user_id,
        payload=payload.model_dump(),
    )
    return db_user


def update_user_password(
    payload: UpdateUserPasswordRequestModel,
    user_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
    slave_db: Session = Depends(get_slave_db),
) -> UpdateUserPasswordResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "user_id": user_id,
            "authorized_user_id": authorized_user_id,
        },
    )
    user_services.update_user(
        write_db=db,
        read_db=slave_db,
        user_id=user_id,
        payload={
            "password": payload.password,
        },
    )
    return UpdateUserPasswordResponseModel(id=user_id)
