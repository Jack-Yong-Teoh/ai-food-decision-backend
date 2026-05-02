from fastapi import APIRouter
from app.models.routes.api_routes import InterceptorAPIRoute
from app.controllers.lucky_pick import (
    get_lucky_pick,
    update_lucky_pick,
    delete_lucky_pick,
    lazyload_lucky_picks,
    create_lucky_pick,
)

router = APIRouter(route_class=InterceptorAPIRoute)
router.add_api_route(
    "",
    create_lucky_pick,
    methods=["POST"],
)
router.add_api_route(
    "s",
    lazyload_lucky_picks,
    methods=["POST"],
)
router.add_api_route(
    "",
    get_lucky_pick,
    methods=["GET"],
)
router.add_api_route(
    "/{lucky_pick_id}",
    update_lucky_pick,
    methods=["PUT"],
)
router.add_api_route(
    "/{lucky_pick_id}",
    delete_lucky_pick,
    methods=["DELETE"],
)
