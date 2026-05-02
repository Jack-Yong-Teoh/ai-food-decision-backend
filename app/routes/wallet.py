from fastapi import APIRouter
from app.models.routes.api_routes import InterceptorAPIRoute
from app.controllers.wallet import (
    get_wallet,
    delete_wallet,
    create_wallet,
    get_wallet_by_user,
)

router = APIRouter(route_class=InterceptorAPIRoute)
router.add_api_route(
    "/user",
    get_wallet_by_user,
    methods=["GET"],
)
router.add_api_route(
    "",
    create_wallet,
    methods=["POST"],
)
router.add_api_route(
    "/{wallet_id}",
    get_wallet,
    methods=["GET"],
)
router.add_api_route(
    "/{wallet_id}",
    delete_wallet,
    methods=["DELETE"],
)
