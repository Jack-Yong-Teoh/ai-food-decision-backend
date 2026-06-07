from datetime import datetime

from app.models.databases.queries.base import LazyLoadResult, QueryResultModel


class DetailedFoodResultModel(QueryResultModel):
    id: int | None = None
    user_id: int | None = None
    food_name: str | None = None
    food_type: str | None = None
    calories: str | None = None
    description: str | None = None
    ingredients: str | None = None
    image_url: str | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None


class LazyloadFoodQueryResultModel(QueryResultModel):
    id: int | None = None
    user_id: int | None = None
    food_name: str | None = None
    food_type: str | None = None
    calories: str | None = None
    description: str | None = None
    ingredients: str | None = None
    image_url: str | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None


class LazyloadFoodResultModel(LazyLoadResult):
    data: list[LazyloadFoodQueryResultModel]
