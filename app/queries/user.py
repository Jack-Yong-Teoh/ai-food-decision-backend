from typing import Optional
from sqlalchemy import BinaryExpression, ColumnOperators, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from app.models.databases.orm.user import User
from app.models.databases.queries.user import LazyloadUserResultModel
from app.models.databases.queries.base import FilterModel, PaginateModel, SortModel
from app.queries.base import lazyload_data
from app.models.exceptions.not_found_exception import NotFoundException


def get_filter_criterion(
    user_id: int = None,
    username: str = None,
    password: str = None,
    first_name: str = None,
    last_name: str = None,
    is_active: bool = None,
    is_superuser: bool = None,
    get_one: bool = True,
) -> list[BinaryExpression]:
    criterion = [
        (None if user_id is None else ColumnOperators.__eq__(User.id, user_id)),
        (
            None
            if username is None
            else ColumnOperators.__eq__(func.lower(User.username), func.lower(username))
        ),
        (None if password is None else ColumnOperators.__eq__(User.password, password)),
        (
            None
            if first_name is None
            else ColumnOperators.__eq__(
                func.lower(User.first_name), func.lower(first_name)
            )
        ),
        (
            None
            if last_name is None
            else ColumnOperators.__eq__(
                func.lower(User.last_name), func.lower(last_name)
            )
        ),
        (
            None
            if is_active is None
            else ColumnOperators.__eq__(User.is_active, is_active)
        ),
        (
            None
            if is_superuser is None
            else ColumnOperators.__eq__(User.is_superuser, is_superuser)
        ),
    ]
    criterion = [x for x in criterion if x is not None]
    if get_one and len(criterion) == 0:
        raise ValueError("No filtering criteria provided")
    return criterion


def get_users(
    db: Session,
    user_id: int = None,
    username: str = None,
    password: str = None,
    first_name: str = None,
    last_name: str = None,
    is_active: bool = None,
    is_superuser: bool = None,
) -> list[User]:
    criterion = get_filter_criterion(
        user_id=user_id,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
        is_superuser=is_superuser,
        get_one=False,
    )
    db_users = db.query(User).filter(*criterion).all()
    return db_users


def get_user(
    db: Session,
    user_id: int = None,
    username: str = None,
    password: str = None,
    first_name: str = None,
    last_name: str = None,
    is_active: bool = None,
    is_superuser: bool = None,
    optional: bool = False,
) -> Optional[User]:
    criterion = get_filter_criterion(
        user_id=user_id,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
        is_superuser=is_superuser,
    )
    db_user = db.query(User).filter(*criterion).one_or_none()
    if db_user is None and not optional:
        raise NotFoundException(
            "USER_NOT_FOUND",
            extra={
                "user_id": user_id,
                "username": username,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": is_active,
                "is_superuser": is_superuser,
            },
        )
    return db_user


def save_user(
    db: Session,
    user: User,
    auto_commit: bool = True,
) -> User:
    db.add(user)
    # pylint: disable-next=expression-not-assigned
    db.commit() if auto_commit else db.flush()
    db.refresh(user)
    return user


async def lazyload_users(
    async_db: AsyncSession,
    filters: list[FilterModel],
    pagination: PaginateModel,
    sort: SortModel,
    search: str = None,
    included_fields: list[str] = None,
    excluded_fields: list[str] = None,
    export: bool = False,
) -> LazyloadUserResultModel:
    select_query = select(
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.is_active,
        User.is_superuser,
        User.last_access,
        User.created_date,
    ).select_from(User)
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
    return LazyloadUserResultModel(**results.__dict__)
