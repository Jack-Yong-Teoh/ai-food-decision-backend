from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.decorators.export import export_async
from app.models.databases.queries.food import (
    DetailedFoodResultModel,
    LazyloadFoodResultModel,
)
from app.models.pydantic_schemas.base import LazyloadRequestModel
from app.models.request_models.food import CreateFoodRequestModel
from app.models.response_models.base import NoContentResponse
from app.models.response_models.food import CreateFoodResponseModel
from app.queries.food import get_food as query_get_food
from app.queries.food import lazyload_foods as query_lazyload_foods
from app.services.authentication import get_authorized_user_id
from app.services import food as food_services
from app.utilities.logger import logger
from app.utilities.postgresql import get_async_slave_db, get_db, get_slave_db


def get_food(
    food_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_slave_db),
) -> DetailedFoodResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "food_id": food_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    db_food = query_get_food(
        db=db,
        food_id=food_id,
    )
    return db_food


def create_food(
    payload: CreateFoodRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> CreateFoodResponseModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "authorized_user_id": authorized_user_id,
        },
    )
    db_food = food_services.create_food(
        write_db=db,
        payload=payload,
        authorized_user_id=authorized_user_id,
    )
    return CreateFoodResponseModel.model_validate(db_food)


def delete_food(
    food_id: int,
    authorized_user_id: int = Depends(get_authorized_user_id),
    db: Session = Depends(get_db),
) -> NoContentResponse:
    logger.debug(
        "Payload Received",
        extra={
            "food_id": food_id,
            "authorized_user_id": authorized_user_id,
        },
    )

    food_services.delete_food(
        write_db=db,
        food_id=food_id,
    )

    return NoContentResponse()


@export_async
async def lazyload_foods(
    payload: LazyloadRequestModel,
    authorized_user_id: int = Depends(get_authorized_user_id),
    async_slave_db: AsyncSession = Depends(get_async_slave_db),
) -> LazyloadFoodResultModel:
    logger.debug(
        "Payload Received",
        extra={
            "payload": payload.model_dump(),
            "authorized_user_id": authorized_user_id,
        },
    )

    return await query_lazyload_foods(
        async_db=async_slave_db,
        filters=payload.filters,
        search=payload.search,
        pagination=payload.pagination,
        sort=payload.sort,
        included_fields=payload.included_fields,
        excluded_fields=payload.excluded_fields,
        export=payload.export,
    )
