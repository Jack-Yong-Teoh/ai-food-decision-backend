from fastapi import APIRouter
from app.models.routes.api_routes import InterceptorAPIRoute
from app.controllers.user import (
    get_user,
    update_user,
    delete_user,
    lazyload_users,
    create_user,
    get_profile,
    update_profile,
    update_user_password,
)

router = APIRouter(route_class=InterceptorAPIRoute)
router.add_api_route(
    "/profile",
    get_profile,
    methods=["GET"],
)
router.add_api_route(
    "/profile",
    update_profile,
    methods=["PUT"],
)
router.add_api_route(
    "",
    create_user,
    methods=["POST"],
)
router.add_api_route(
    "s",
    lazyload_users,
    methods=["POST"],
)
router.add_api_route(
    "",
    get_user,
    methods=["GET"],
)
router.add_api_route(
    "/{user_id}",
    update_user,
    methods=["PUT"],
)
router.add_api_route(
    "/{user_id}",
    delete_user,
    methods=["DELETE"],
)
router.add_api_route(
    "/{user_id}/password",
    update_user_password,
    methods=["PUT"],
)
