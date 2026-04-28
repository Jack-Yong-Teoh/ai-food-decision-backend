import json
import time
import uuid
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.datastructures import MutableHeaders
from app.services.authentication import decode_token
from app.utilities.contextvar import (
    contextvar_correlation_id,
    contextvar_locale,
    contextvar_session_user_id,
    contextvar_endpoint,
)
from app.utilities.logger import logger
from app.utilities.config import CONFIG


def __payload_sanitizer(key, value):
    if "password" in key.lower():
        return "".join(["*" for _ in range(len(value))])
    return value


def get_request_template_path(request: Request):
    path = request.url.path
    for k, v in request.path_params.items():
        path = path.replace(f"/{v}", f"/{{{k}}}")
    return path


async def get_request_body(
    request: Request,
    sanitize: bool = False,
):
    request_body = None
    try:
        request_body = await request.body()
        try:
            request_body = json.loads(request_body)
            if sanitize:
                request_body = {
                    k: __payload_sanitizer(k, v) for k, v in request_body.items()
                }
        except:
            pass
    except:
        pass
    return request_body


def get_token_model(request: Request):
    try:
        authorization = request.headers.get("authorization")
        if authorization:
            token = authorization.split(" ")[1]
            token_model = decode_token(
                token,
                raise_error=False,
            )
            return token_model
    except:
        pass
    return None


def handle_pre_correlation(request: Request):
    prefix = CONFIG.OTHER.HEADER_PREFIX
    correlation_id_key = f"{prefix}-Correlation-ID"
    header_correlation_id = request.headers.get(correlation_id_key)
    correlation_id = (
        header_correlation_id if header_correlation_id else str(uuid.uuid4())
    )
    headers = MutableHeaders(request.headers)
    headers[correlation_id_key] = correlation_id
    request.scope.update(headers=headers.raw)
    contextvar_correlation_id.set(correlation_id)
    contextvar_endpoint.set(f"{request.method} - {request.url}")

    logger.debug(
        "Correlation ID Interceptor",
        extra={
            "correlation_id": correlation_id,
        },
    )
    return correlation_id


def handle_post_correlation(
    response: Response,
    correlation_id: str,
):
    prefix = CONFIG.OTHER.HEADER_PREFIX
    response.headers[f"{prefix}-Correlation-ID"] = correlation_id


def handle_pre_process_time():
    start_time = time.time()
    return start_time


def handle_post_process_time(
    response: Response,
    start_time: float,
):
    prefix = CONFIG.OTHER.HEADER_PREFIX
    process_time = time.time() - start_time
    response.headers[f"{prefix}-Process-Time"] = str(process_time)

    logger.debug(
        "Process Time Interceptor",
        extra={
            "process_time": str(process_time),
        },
    )


async def log_request(request: Request):
    request_headers = request.headers
    decoded_token = None
    request_body = await get_request_body(
        request=request,
        sanitize=True,
    )
    request_form = None

    token_model = get_token_model(request)
    decoded_token = token_model.dict() if token_model else None

    try:
        request_form = await request.form()
    except:
        pass

    logger.debug(
        "Request Details",
        extra={
            "headers": request_headers,
            "decoded_token": decoded_token,
            "payload": request_body,
            "form": request_form,
        },
    )


def handle_response(
    request: Request,
    response: Response,
):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    log_response(request, response)


def handle_locale(request: Request):
    accept_language = request.headers.get("accept-language")
    if accept_language:
        contextvar_locale.set(accept_language)


def handle_session_user(request: Request):
    token_model = get_token_model(request)
    contextvar_session_user_id.set(token_model.user_id if token_model else None)


def log_response(
    request: Request,
    response: Response,
):
    if not isinstance(response, Response) or isinstance(response, StreamingResponse):
        logger.warning(
            "Unable To Log Response Details",
            extra={
                "response": response,
            },
        )
        return

    # pylint: disable=line-too-long
    exclude_endpoints = []
    # pylint: enable=line-too-long

    path = get_request_template_path(request)
    matched_endpoints = [
        x
        for x in exclude_endpoints
        if x["method"] == request.method and x["path"] == path
    ]
    if any(matched_endpoints):
        logger.warning(
            "Skip Response Details",
            extra={
                "method": request.method,
                "path": path,
                "matched_endpoints": matched_endpoints,
                "status_code": response.status_code,
            },
        )
        return

    response_body = None
    try:
        response_body = json.loads(response.body)
    except:
        response_body = response.body

    logger.debug(
        "Response Details",
        extra={
            "status_code": response.status_code,
            "body": response_body,
        },
    )
