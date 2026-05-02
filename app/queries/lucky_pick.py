from typing import Optional
from sqlalchemy import BinaryExpression, ColumnOperators, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from app.models.databases.orm.lucky_pick import LuckyPick
from app.models.databases.queries.lucky_pick import LazyloadLuckyPickResultModel
from app.models.databases.queries.base import FilterModel, PaginateModel, SortModel
from app.queries.base import lazyload_data
from app.models.exceptions.not_found_exception import NotFoundException


def get_filter_criterion(
    lucky_pick_id: int = None,
    option_name: str = None,
    description: str = None,
    get_one: bool = True,
) -> list[BinaryExpression]:
    criterion = [
        (
            None
            if lucky_pick_id is None
            else ColumnOperators.__eq__(LuckyPick.id, lucky_pick_id)
        ),
        (
            None
            if option_name is None
            else ColumnOperators.__eq__(
                func.lower(LuckyPick.option_name), func.lower(option_name)
            )
        ),
        (
            None
            if description is None
            else ColumnOperators.__eq__(
                func.lower(LuckyPick.description), func.lower(description)
            )
        ),
    ]
    criterion = [x for x in criterion if x is not None]
    if get_one and len(criterion) == 0:
        raise ValueError("No filtering criteria provided")
    return criterion


def get_lucky_picks(
    db: Session,
    lucky_pick_id: int = None,
    option_name: str = None,
    description: str = None,
) -> list[LuckyPick]:
    criterion = get_filter_criterion(
        lucky_pick_id=lucky_pick_id,
        option_name=option_name,
        description=description,
        get_one=False,
    )
    db_lucky_picks = db.query(LuckyPick).filter(*criterion).all()
    return db_lucky_picks


def get_lucky_pick(
    db: Session,
    lucky_pick_id: int = None,
    option_name: str = None,
    description: str = None,
    optional: bool = False,
) -> Optional[LuckyPick]:
    criterion = get_filter_criterion(
        lucky_pick_id=lucky_pick_id,
        option_name=option_name,
        description=description,
    )
    db_lucky_pick = db.query(LuckyPick).filter(*criterion).one_or_none()
    if db_lucky_pick is None and not optional:
        raise NotFoundException(
            "LUCKY_PICK_NOT_FOUND",
            extra={
                "lucky_pick_id": lucky_pick_id,
                "option_name": option_name,
                "description": description,
            },
        )
    return db_lucky_pick


def save_lucky_pick(
    db: Session,
    lucky_pick: LuckyPick,
    auto_commit: bool = True,
) -> LuckyPick:
    db.add(lucky_pick)
    # pylint: disable-next=expression-not-assigned
    db.commit() if auto_commit else db.flush()
    db.refresh(lucky_pick)
    return lucky_pick


async def lazyload_lucky_picks(
    async_db: AsyncSession,
    filters: list[FilterModel],
    pagination: PaginateModel,
    sort: SortModel,
    search: str = None,
    included_fields: list[str] = None,
    excluded_fields: list[str] = None,
    export: bool = False,
) -> LazyloadLuckyPickResultModel:
    select_query = select(
        LuckyPick.id,
        LuckyPick.option_name,
        LuckyPick.description,
        LuckyPick.created_date,
        LuckyPick.modified_date,
    ).select_from(LuckyPick)
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
    return LazyloadLuckyPickResultModel(**results.__dict__)
