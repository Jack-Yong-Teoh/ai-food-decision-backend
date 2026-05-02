from sqlalchemy.orm import Session
from app.models.databases.orm.user import User
from app.models.exceptions.conflict_exception import ConflictException
from app.models.exceptions.logic_exception import LogicException
from app.queries.user import get_user, save_user
from app.utilities.error_message import conflict_error, incorrect_value
from app.utilities.logger import logger


def before_save_validation(
    read_db: Session,
    user: User,
) -> None:
    db_user = get_user(
        db=read_db,
        username=user.username,
        optional=True,
    )
    if db_user and db_user.id != user.id:
        raise ConflictException(
            conflict_error(field_name="USERNAME"),
            extra={
                "username": user.username,
                "db_user": db_user,
            },
        )


def create_user(
    write_db: Session,
    read_db: Session,
    user: User,
    auto_commit: bool = True,
) -> User:
    before_save_validation(
        read_db=read_db,
        user=user,
    )

    db_user = save_user(db=write_db, user=user, auto_commit=False)

    logger.debug(
        "User Created",
        extra={
            "db_user": db_user,
        },
    )

    if auto_commit:
        write_db.commit()
        write_db.refresh(db_user)

    return db_user


def delete_user(
    write_db: Session,
    user_id: int,
    auto_commit: bool = True,
) -> None:
    db_user = get_user(
        db=write_db,
        user_id=user_id,
    )

    write_db.delete(db_user)

    if auto_commit:
        write_db.commit()

    logger.debug(
        "User Deleted",
        extra={
            "db_user": db_user,
        },
    )


def update_user(
    write_db: Session,
    read_db: Session,
    user_id: int,
    payload: dict,
    auto_commit: bool = True,
) -> User:
    db_user = get_user(
        db=write_db,
        user_id=user_id,
    )

    for key, value in payload.items():
        setattr(db_user, key, value)

    before_save_validation(
        read_db=read_db,
        user=db_user,
    )

    db_user = save_user(db=write_db, user=db_user, auto_commit=False)

    logger.debug(
        "User Updated",
        extra={
            "db_user": db_user,
        },
    )

    if auto_commit:
        write_db.commit()
        write_db.refresh(db_user)

    return db_user


def update_password(
    write_db: Session,
    read_db: Session,
    user_id: int,
    current_password: str,
    new_password: str,
) -> None:
    db_user = get_user(
        db=read_db,
        user_id=user_id,
    )

    if current_password != db_user.password:
        raise LogicException(
            incorrect_value(field_name="PASSWORD"),
            extra={
                "user_id": user_id,
            },
        )

    update_user(
        write_db=write_db,
        read_db=read_db,
        user_id=user_id,
        payload={
            "password": new_password,
        },
    )
