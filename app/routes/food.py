from fastapi import APIRouter

from app.controllers.food import create_food, delete_food, get_food, lazyload_foods
from app.models.routes.api_routes import InterceptorAPIRoute

router = APIRouter(route_class=InterceptorAPIRoute)
router.add_api_route(
    "",
    create_food,
    methods=["POST"],
)
router.add_api_route(
    "s",
    lazyload_foods,
    methods=["POST"],
)
router.add_api_route(
    "/{food_id}",
    get_food,
    methods=["GET"],
)
router.add_api_route(
    "/{food_id}",
    delete_food,
    methods=["DELETE"],
)
