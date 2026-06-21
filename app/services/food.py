import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from app.models.databases.orm.food import Food
from app.models.databases.orm.transaction import Transaction
from app.models.enums.transaction import TransactionType
from app.models.exceptions.forbidden_exception import ForbiddenException
from app.models.exceptions.integration_exception import IntegrationException
from app.models.request_models.food import CreateFoodRequestModel
from app.queries.user import get_user
from app.queries.food import get_food, save_food
from app.services.transaction import create_transaction as create_transaction_service
from app.utilities.config import CONFIG
from app.utilities.error_message import general_error
from app.utilities.logger import logger


def _build_food_prompt(payload: CreateFoodRequestModel) -> str:
    return (
        "Generate one food recommendation in valid JSON only. "
        "Return an object with these keys: food_name, food_type, calories, description, "
        "ingredients. The ingredients field must contain ingredient names only, "
        "with no quantities, measurements, prep steps, descriptors, or parenthetical notes. "
        "Return ingredients as a list of plain ingredient names. Do not include markdown, "
        "comments, or extra keys. "
        "Use the user's preferences below. "
        f"food_type={payload.food_type}; "
        f"meal_type={payload.meal_type}; "
        f"dietary_restriction={payload.dietary_restriction}; "
        f"mood={payload.mood}; "
        f"additional_notes={payload.additional_notes}"
    )


def _slugify_food_name(food_name: str) -> str:
    return "-".join(food_name.strip().split()).lower()


def _normalize_ingredients(ingredients: object) -> str | None:
    if ingredients is None:
        return None

    if isinstance(ingredients, list):
        items = [str(item).strip() for item in ingredients if str(item).strip()]
    elif isinstance(ingredients, str):
        raw_value = ingredients.strip()
        if not raw_value:
            return None

        try:
            parsed_value = json.loads(raw_value)
        except (TypeError, json.JSONDecodeError):
            parsed_value = None

        if isinstance(parsed_value, list):
            items = [str(item).strip() for item in parsed_value if str(item).strip()]
        else:
            if raw_value.startswith("{") and raw_value.endswith("}"):
                raw_value = raw_value[1:-1]
            items = [
                item.strip().strip('"').strip("'")
                for item in raw_value.split(",")
                if item.strip()
            ]
    else:
        items = [str(ingredients).strip()]

    normalized_items = [item for item in items if item]

    return "{" + ", ".join(normalized_items) + "}"


def _extract_json_object(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.lower().startswith("json"):
            content = content[4:].strip()
    start_index = content.find("{")
    end_index = content.rfind("}")
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise ValueError("AI RESPONSE IS NOT VALID JSON")
    return json.loads(content[start_index : end_index + 1])


def _call_openai_compatible_api(payload: CreateFoodRequestModel) -> dict:
    api_key = CONFIG.OPENAI.API_KEY
    base_url = CONFIG.OPENAI.BASE_URL
    model = CONFIG.OPENAI.MODEL
    timeout = float(CONFIG.OPENAI.TIMEOUT or 30)

    if not api_key or not base_url or not model:
        raise IntegrationException(
            general_error("OPENAI CONFIGURATION IS NOT COMPLETE"),
            extra={
                "has_api_key": bool(api_key),
                "base_url": base_url,
                "model": model,
            },
        )

    request_body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a food recommendation engine. Return only valid JSON and "
                    "make the response compatible with a food record."
                ),
            },
            {"role": "user", "content": _build_food_prompt(payload)},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    request = Request(
        urljoin(base_url.rstrip("/") + "/", "chat/completions"),
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else None
        raise IntegrationException(
            general_error("AI GENERATION FAILED"),
            extra={
                "status_code": exc.code,
                "body": error_body,
            },
        ) from exc
    except URLError as exc:
        raise IntegrationException(
            general_error("AI GENERATION FAILED"),
            extra={
                "reason": str(exc.reason),
            },
        ) from exc

    try:
        content = response_payload["choices"][0]["message"]["content"]
        return _extract_json_object(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise IntegrationException(
            general_error("AI RESPONSE FORMAT IS INVALID"),
            extra={
                "response": response_payload,
            },
        ) from exc


def _call_pixabay_api(food_name: str, food_type: str) -> str:
    api_key = CONFIG.PIXABAY.API_KEY
    base_url = CONFIG.PIXABAY.BASE_URL
    timeout = float(CONFIG.PIXABAY.TIMEOUT or 30)

    if not api_key or not base_url:
        raise IntegrationException(
            general_error("PIXABAY CONFIGURATION IS NOT COMPLETE"),
            extra={
                "has_api_key": bool(api_key),
                "base_url": base_url,
            },
        )

    query_params = urlencode(
        {
            "key": api_key,
            "q": _slugify_food_name(f"{food_name} {food_type}"),
            "image_type": "photo",
            "per_page": 3,
        }
    )
    request = Request(
        f"{base_url.rstrip('?')}{'?' if '?' not in base_url else '&'}{query_params}"
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc.fp else None
        raise IntegrationException(
            general_error("IMAGE LOOKUP FAILED"),
            extra={
                "status_code": exc.code,
                "body": error_body,
            },
        ) from exc
    except URLError as exc:
        raise IntegrationException(
            general_error("IMAGE LOOKUP FAILED"),
            extra={
                "reason": str(exc.reason),
            },
        ) from exc

    try:
        return response_payload["hits"][0]["webformatURL"]
    except (KeyError, IndexError, TypeError) as exc:
        raise IntegrationException(
            general_error("PIXABAY RESPONSE FORMAT IS INVALID"),
            extra={
                "response": response_payload,
            },
        ) from exc


def create_food(
    write_db: Session,
    payload: CreateFoodRequestModel,
    authorized_user_id: int,
    auto_commit: bool = True,
) -> Food:
    db_user = get_user(
        db=write_db,
        user_id=authorized_user_id,
    )
    if db_user.wallet_id is None:
        raise ForbiddenException(
            general_error("WALLET NOT FOUND"),
            extra={
                "user_id": authorized_user_id,
            },
        )

    generated_food = _call_openai_compatible_api(payload)
    generated_food["image_url"] = _call_pixabay_api(
        generated_food["food_name"],
        generated_food["food_type"],
    )
    generated_food["ingredients"] = _normalize_ingredients(
        generated_food.get("ingredients")
    )
    db_food = Food(
        user_id=authorized_user_id,
        **generated_food,
    )

    try:
        save_food(
            db=write_db,
            food=db_food,
            auto_commit=False,
        )

        create_transaction_service(
            write_db=write_db,
            transaction=Transaction(
                wallet_id=db_user.wallet_id,
                amount=payload.token_consumed,
                transaction_type=TransactionType.PAYMENT,
                reference_id=f"food:{db_food.id}",
            ),
            authorized_user_id=authorized_user_id,
            auto_commit=False,
        )

        if auto_commit:
            write_db.commit()
            write_db.refresh(db_food)

    except Exception:
        write_db.rollback()
        raise

    logger.debug(
        "Food Created",
        extra={
            "db_food": db_food,
        },
    )
    return db_food


def delete_food(
    write_db: Session,
    food_id: int,
    auto_commit: bool = True,
) -> None:
    db_food = get_food(
        db=write_db,
        food_id=food_id,
    )
    write_db.delete(db_food)

    if auto_commit:
        write_db.commit()

    logger.debug(
        "Food Deleted",
        extra={
            "db_food": db_food,
        },
    )
