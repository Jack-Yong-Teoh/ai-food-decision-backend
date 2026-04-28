from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.exceptions import HTTPException, RequestValidationError
from app.models.exceptions import LogicException
from app.middlewares.utilities import (
    handle_pre_correlation,
    handle_post_correlation,
    handle_pre_process_time,
    handle_post_process_time,
    handle_response,
    handle_locale,
    handle_session_user,
)
from app.models.response_models.exceptions import (
    LogicExceptionHandler,
    HTTPExceptionHandler,
    ExceptionHandler,
    RequestValidationErrorHandler,
)


class InterceptorAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            correlation_id = handle_pre_correlation(request)
            start_time = handle_pre_process_time()
            handle_locale(request)
            handle_session_user(request)

            response = None
            try:
                response: Response = await original_route_handler(request)

            except LogicException as e:
                response: Response = await LogicExceptionHandler.handler(request, e)

            except HTTPException as e:
                response: Response = await HTTPExceptionHandler.handler(request, e)

            except RequestValidationError as e:
                response: Response = await RequestValidationErrorHandler.handler(
                    request, e
                )

            except Exception as e:
                response: Response = await ExceptionHandler.handler(request, e)

            finally:
                handle_post_correlation(response, correlation_id)
                handle_response(request, response)
                handle_post_process_time(response, start_time)

            # pylint: disable-next=lost-exception
            return response

        return custom_route_handler
