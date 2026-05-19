from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.decorators.export import export_async
from app.models.pydantic_schemas.base import LazyloadRequestModel
from app.models.request_models.lucky_pick import (
    UpdateLuckyPickRequestModel,
    CreateLuckyPickRequestModel,
)
from app.models.response_models.base import NoContentResponse
from app.models.response_models.lucky_pick import (
    UpdateLuckyPickResponseModel,
    CreateLuckyPickResponseModel,
)
from app.models.databases.orm.lucky_pick import LuckyPick
from app.models.databases.queries.lucky_pick import (
    DetailedLuckyPickResultModel,
    LazyloadLuckyPickResultModel,
)
from app.queries.lucky_pick import (
    get_lucky_pick as query_get_lucky_pick,
    lazyload_lucky_picks as query_lazyload_lucky_picks,
)
from app.services.authentication import get_authorized_user_id
from app.services import lucky_pick as lucky_pick_services
from app.utilities.logger import logger
from app.utilities.postgresql import get_db, get_slave_db, get_async_slave_db


def get_lucky_pick(
    lucky_pick_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_slave_db),
) -> DetailedLuckyPickResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "lucky_pick_id": lucky_pick_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    db_lucky_pick = query_get_lucky_pick(
        db=db,
        lucky_pick_id=lucky_pick_id,
    )

    return db_lucky_pick


def create_lucky_pick(
    payload: CreateLuckyPickRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> CreateLuckyPickResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "authorized_user_id": authorized_user_id,
        },
    )
    db_lucky_pick = lucky_pick_services.create_lucky_pick(
        write_db=db,
        lucky_pick=LuckyPick(**payload.model_dump()),
    )
    return db_lucky_pick


def update_lucky_pick(
    lucky_pick_id: int,
    payload: UpdateLuckyPickRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> UpdateLuckyPickResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(exclude_none=True),
            "lucky_pick_id": lucky_pick_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    db_lucky_pick = lucky_pick_services.update_lucky_pick(
        write_db=db,
        lucky_pick_id=lucky_pick_id,
        payload=payload.model_dump(exclude_none=True),
    )

    return UpdateLuckyPickResponseModel(id=db_lucky_pick.id)


def delete_lucky_pick(
    lucky_pick_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> NoContentResponse:
    logger.debug(
        "Payload Received",
        extra={
            "lucky_pick_id": lucky_pick_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    lucky_pick_services.delete_lucky_pick(
        write_db=db,
        lucky_pick_id=lucky_pick_id,
    )

    return NoContentResponse()


@export_async
async def lazyload_lucky_picks(
    payload: LazyloadRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    async_slave_db: AsyncSession = Depends(get_async_slave_db),
) -> LazyloadLuckyPickResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "authorized_user_id": authorized_user_id,
        },
    )

    return await query_lazyload_lucky_picks(
        async_db=async_slave_db,
        filters=payload.filters,
        search=payload.search,
        pagination=payload.pagination,
        sort=payload.sort,
        included_fields=payload.included_fields,
        excluded_fields=payload.excluded_fields,
        export=payload.export,
    )
