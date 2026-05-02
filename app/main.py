from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.middlewares.utilities import log_request
from app.models.response_models.exceptions.http_exception_handler import (
    HTTPExceptionHandler,
    LogicExceptionHandler,
    ExceptionHandler,
    RequestValidationErrorHandler,
)
from app.utilities.config import CONFIG
from app.utilities.postgresql import engine
from app.models.response_templates import exceptions
from app.models.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    LogicException,
)
from app.routes import (
    authentication,
    user,
    lucky_pick,
    wallet,
)

fastapi_kwargs = (
    {"docs_url": None, "redoc_url": None} if CONFIG.OTHER.APP_ENV == "prod" else {}
)
app = FastAPI(
    **fastapi_kwargs,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=CONFIG.OTHER.ALLOW_ORIGIN.split(","),
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
    ],
    exception_handlers={
        LogicException: LogicExceptionHandler.handler,
        Exception: ExceptionHandler.handler,
        SQLAlchemyError: ExceptionHandler.handler,
    },
    responses=exceptions.responses(
        [
            Exception,
            LogicException,
            ForbiddenException,
            UnauthorizedException,
            NotFoundException,
            ConflictException,
        ]
    ),
    dependencies=[Depends(log_request)],
)

# API Routes
app.add_exception_handler(RequestValidationError, RequestValidationErrorHandler.handler)
app.add_exception_handler(HTTPException, HTTPExceptionHandler.handler)

app.include_router(
    authentication.router,
    prefix="/api/authentication",
    tags=["authentication"],
)

app.include_router(
    user.router,
    prefix="/api/user",
    tags=["users"],
)

app.include_router(
    lucky_pick.router,
    prefix="/api/lucky-pick",
    tags=["lucky-picks"],
)

app.include_router(
    wallet.router,
    prefix="/api/wallet",
    tags=["wallets"],
)
