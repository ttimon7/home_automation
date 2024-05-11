import logging

from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.infrastructure.fast_api_utils import APIRouter

logger = logging.getLogger(__name__)


def get_prefix() -> str:
    return f"{configuration.api.api_prefix}"


def get_root_endpoint() -> APIRouter:
    router = APIRouter(prefix=get_prefix())

    @router.get("/")
    def read_root() -> dict[str, str]:
        return {"message": "Welcome to the LED Controller API"}

    return router
