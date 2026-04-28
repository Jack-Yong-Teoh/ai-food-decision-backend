from fastapi import APIRouter
from app.models.routes.api_routes import InterceptorAPIRoute
from app.controllers.authentication import login, logout, refresh_token, change_password

router = APIRouter(route_class=InterceptorAPIRoute)
router.add_api_route(
    "/login",
    login,
    methods=["POST"],
)
router.add_api_route(
    "/logout",
    logout,
    methods=["POST"],
)
router.add_api_route(
    "/token/refresh",
    refresh_token,
    methods=["POST"],
)
router.add_api_route(
    "/password/change",
    change_password,
    methods=["PUT"],
)
