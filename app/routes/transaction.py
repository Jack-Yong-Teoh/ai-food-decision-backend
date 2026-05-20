from fastapi import APIRouter

from app.controllers.transaction import (
    create_transaction,
    lazyload_transactions,
    get_transaction,
)
from app.models.routes.api_routes import InterceptorAPIRoute

router = APIRouter(route_class=InterceptorAPIRoute)
router.add_api_route(
    "",
    create_transaction,
    methods=["POST"],
)
router.add_api_route(
    "s",
    lazyload_transactions,
    methods=["POST"],
)
router.add_api_route(
    "",
    get_transaction,
    methods=["GET"],
)
