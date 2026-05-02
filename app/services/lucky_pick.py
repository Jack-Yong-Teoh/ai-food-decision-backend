from sqlalchemy.orm import Session
from app.models.databases.orm.lucky_pick import LuckyPick
from app.queries.lucky_pick import get_lucky_pick, save_lucky_pick
from app.utilities.logger import logger


def create_lucky_pick(
    write_db: Session,
    lucky_pick: LuckyPick,
    auto_commit: bool = True,
) -> LuckyPick:
    db_lucky_pick = save_lucky_pick(db=write_db, lucky_pick=lucky_pick, auto_commit=False)

    logger.debug(
        "Lucky Pick Created",
        extra={
            "db_lucky_pick": db_lucky_pick,
        },
    )

    if auto_commit:
        write_db.commit()
        write_db.refresh(db_lucky_pick)

    return db_lucky_pick


def delete_lucky_pick(
    write_db: Session,
    lucky_pick_id: int,
    auto_commit: bool = True,
) -> None:
    db_lucky_pick = get_lucky_pick(
        db=write_db,
        lucky_pick_id=lucky_pick_id,
    )

    write_db.delete(db_lucky_pick)

    if auto_commit:
        write_db.commit()

    logger.debug(
        "Lucky Pick Deleted",
        extra={
            "db_lucky_pick": db_lucky_pick,
        },
    )


def update_lucky_pick(
    write_db: Session,
    lucky_pick_id: int,
    payload: dict,
    auto_commit: bool = True,
) -> LuckyPick:
    db_lucky_pick = get_lucky_pick(
        db=write_db,
        lucky_pick_id=lucky_pick_id,
    )

    for key, value in payload.items():
        setattr(db_lucky_pick, key, value)

    db_lucky_pick = save_lucky_pick(
        db=write_db,
        lucky_pick=db_lucky_pick,
        auto_commit=False,
    )

    logger.debug(
        "Lucky Pick Updated",
        extra={
            "db_lucky_pick": db_lucky_pick,
        },
    )

    if auto_commit:
        write_db.commit()
        write_db.refresh(db_lucky_pick)

    return db_lucky_pick