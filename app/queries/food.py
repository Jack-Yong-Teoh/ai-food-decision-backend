from typing import Optional

from sqlalchemy import BinaryExpression, ColumnOperators, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from app.models.databases.orm.food import Food
from app.models.databases.queries.base import FilterModel, PaginateModel, SortModel
from app.models.databases.queries.food import LazyloadFoodResultModel
from app.models.exceptions.not_found_exception import NotFoundException
from app.queries.base import lazyload_data


def get_filter_criterion(
    food_id: int = None,
    user_id: int = None,
    food_name: str = None,
    food_type: str = None,
    calories: str = None,
    get_one: bool = True,
) -> list[BinaryExpression]:
    criterion = [
        (None if food_id is None else ColumnOperators.__eq__(Food.id, food_id)),
        (None if user_id is None else ColumnOperators.__eq__(Food.user_id, user_id)),
        (
            None
            if food_name is None
            else ColumnOperators.__eq__(
                func.lower(Food.food_name), func.lower(food_name)
            )
        ),
        (
            None
            if food_type is None
            else ColumnOperators.__eq__(
                func.lower(Food.food_type), func.lower(food_type)
            )
        ),
        (
            None
            if calories is None
            else ColumnOperators.__eq__(func.lower(Food.calories), func.lower(calories))
        ),
    ]
    criterion = [x for x in criterion if x is not None]
    if get_one and len(criterion) == 0:
        raise ValueError("No filtering criteria provided")
    return criterion


def get_foods(
    db: Session,
    food_id: int = None,
    user_id: int = None,
    food_name: str = None,
    food_type: str = None,
    calories: str = None,
) -> list[Food]:
    criterion = get_filter_criterion(
        food_id=food_id,
        user_id=user_id,
        food_name=food_name,
        food_type=food_type,
        calories=calories,
        get_one=False,
    )
    db_foods = db.query(Food).filter(*criterion).all()
    return db_foods


def get_food(
    db: Session,
    food_id: int = None,
    user_id: int = None,
    food_name: str = None,
    food_type: str = None,
    calories: str = None,
    optional: bool = False,
) -> Optional[Food]:
    criterion = get_filter_criterion(
        food_id=food_id,
        user_id=user_id,
        food_name=food_name,
        food_type=food_type,
        calories=calories,
    )
    db_food = db.query(Food).filter(*criterion).one_or_none()
    if db_food is None and not optional:
        raise NotFoundException(
            "FOOD_NOT_FOUND",
            extra={
                "food_id": food_id,
                "user_id": user_id,
                "food_name": food_name,
                "food_type": food_type,
                "calories": calories,
            },
        )
    return db_food


def save_food(
    db: Session,
    food: Food,
    auto_commit: bool = True,
) -> Food:
    db.add(food)
    # pylint: disable-next=expression-not-assigned
    db.commit() if auto_commit else db.flush()
    db.refresh(food)
    return food


def delete_food(
    db: Session,
    food_id: int,
    auto_commit: bool = True,
) -> None:
    db_food = get_food(db=db, food_id=food_id)
    db.delete(db_food)
    if auto_commit:
        db.commit()


async def lazyload_foods(
    async_db: AsyncSession,
    filters: list[FilterModel],
    pagination: PaginateModel,
    sort: SortModel,
    search: str = None,
    included_fields: list[str] = None,
    excluded_fields: list[str] = None,
    export: bool = False,
) -> LazyloadFoodResultModel:
    select_query = select(
        Food.id,
        Food.user_id,
        Food.food_name,
        Food.food_type,
        Food.calories,
        Food.description,
        Food.ingredients,
        Food.image_url,
        Food.created_date,
        Food.modified_date,
    ).select_from(Food)
    results = await lazyload_data(
        async_db=async_db,
        select_query=select_query,
        filters=filters,
        pagination=pagination,
        sort=sort,
        search=search,
        included_fields=included_fields,
        excluded_fields=excluded_fields,
        export=export,
    )
    return LazyloadFoodResultModel(**results.__dict__)
