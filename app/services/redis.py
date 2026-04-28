import json
from typing import Optional
from redis import Redis
from app.models.services.redis import (
    AccessTokenModel,
    RefreshTokenModel,
    UserTokenModel,
)
from app.utilities.logger import logger

KEY_PREFIX = "afd-"


def key_exists(
    redis: Redis,
    key: str,
    append_prefix: bool = True,
) -> bool:
    search_key = f"{KEY_PREFIX}{key}" if append_prefix else key
    result = redis.exists(search_key)
    logger.debug(
        "Key Exists",
        extra={
            "key": key,
            "search_key": search_key,
            "result": result,
        },
    )
    return bool(result)


def get_parsed_value(
    redis: Redis,
    key: str,
    append_prefix: bool = True,
    to_json: bool = True,
) -> any:
    search_key = f"{KEY_PREFIX}{key}" if append_prefix else key
    result = redis.get(search_key)
    logger.debug(
        "Get Parsed Value",
        extra={
            "key": key,
            "search_key": search_key,
            "result": f"{str(result)[0:999]}..." if len(str(result)) > 999 else result,
        },
    )
    if result is None or len(result) == 0:
        return None

    if to_json:
        return json.loads(result)
    return result


def handle_login_success(
    redis: Redis,
    user_id: str,
    access_token: str,
    refresh_token: str = None,
):
    access_token_exp_hours = 24
    access_token_exp_seconds = access_token_exp_hours * 3600
    refresh_token_exp_days = 30
    refresh_token_exp_seconds = refresh_token_exp_days * 24 * 3600

    pipeline = redis.pipeline()
    # Key to invalidate by access token
    pipeline.set(
        name=f"{KEY_PREFIX}{access_token}",
        value=json.dumps(
            AccessTokenModel(
                user_id=user_id,
                refresh_token=refresh_token,
            ).model_dump()
        ),
        ex=access_token_exp_seconds,
    )
    # Key to invalidate by refresh token
    if refresh_token:
        pipeline.set(
            name=f"{KEY_PREFIX}{refresh_token}",
            value=json.dumps(
                RefreshTokenModel(
                    user_id=user_id,
                    access_token=access_token,
                ).model_dump()
            ),
            ex=refresh_token_exp_seconds,
        )
    # Key to invalidate by user ID
    pipeline.set(
        name=f"{KEY_PREFIX}{access_token}-token-{user_id}",
        value=json.dumps(
            UserTokenModel(
                access_token=access_token,
                refresh_token=refresh_token,
            ).model_dump()
        ),
        ex=access_token_exp_seconds,
    )
    results = pipeline.execute()

    logger.debug(
        "Handle Login Success",
        extra={
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "results": results,
        },
    )


def handle_logout_success(
    redis: Redis,
    user_id: str,
    access_token: Optional[str] = None,
):
    if not access_token:
        search_key = f"{KEY_PREFIX}*-token-{user_id}"
        keys = list(redis.scan_iter(match=search_key, count=1_000))
        values = redis.mget(keys)

        logger.debug(
            "Handle Logout Success - Without Token",
            extra={
                "user_id": user_id,
                "search_key": search_key,
                "keys": keys,
                "values": values,
            },
        )

        if values:
            pipeline = redis.pipeline()
            for x in values:
                result = json.loads(x)
                token_model = UserTokenModel(**result)
                pipeline.delete(f"{KEY_PREFIX}{token_model.access_token}")
                pipeline.delete(f"{KEY_PREFIX}{token_model.refresh_token}")
                pipeline.delete(
                    f"{KEY_PREFIX}{token_model.access_token}-token-{user_id}"
                )
                results = pipeline.execute()

                logger.debug(
                    "Handle Logout Success",
                    extra={
                        "user_id": user_id,
                        "access_token": token_model.access_token,
                        "token_model": token_model,
                        "results": results,
                    },
                )
        return

    # To get access token & refresh token
    result = get_parsed_value(
        redis=redis,
        key=f"{access_token}-token-{user_id}",
    )
    logger.debug(
        "Handle Logout Success - With Token",
        extra={
            "user_id": user_id,
            "access_token": access_token,
            "result": result,
        },
    )

    if result:
        token_model = UserTokenModel(**result)
        pipeline = redis.pipeline()
        pipeline.delete(f"{KEY_PREFIX}{token_model.access_token}")
        pipeline.delete(f"{KEY_PREFIX}{token_model.refresh_token}")
        pipeline.delete(f"{KEY_PREFIX}{access_token}-token-{user_id}")
        results = pipeline.execute()

        logger.debug(
            "Handle Logout Success",
            extra={
                "user_id": user_id,
                "access_token": access_token,
                "token_model": token_model,
                "results": results,
            },
        )


def invalidate_refreshed_session(
    redis: Redis,
    refresh_token: str,
):
    pipeline = redis.pipeline()
    pipeline.delete(f"{KEY_PREFIX}{refresh_token}")

    # Delete tokens generated upon success login
    token_model = None
    result = get_parsed_value(
        redis=redis,
        key=refresh_token,
    )
    if result:
        token_model = RefreshTokenModel(**result)
        # Delete access token
        pipeline.delete(f"{KEY_PREFIX}{token_model.access_token}")
        # Delete user tokens mapping
        pipeline.delete(
            f"{KEY_PREFIX}{token_model.access_token}-token-{token_model.user_id}"
        )
    results = pipeline.execute()

    logger.debug(
        "Invalidate Refreshed Session",
        extra={
            "refresh_token": refresh_token,
            "token_model": token_model,
            "results": results,
        },
    )
