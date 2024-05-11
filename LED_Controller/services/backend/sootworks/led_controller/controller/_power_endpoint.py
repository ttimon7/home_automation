import logging

from dependency_injector.wiring import Provide, inject
from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.containers import Container
from sootworks.led_controller.domain.exception import translate_service_exceptions
from sootworks.led_controller.infrastructure.fast_api_utils import APIRouter
from sootworks.led_controller.service import LedControllerService

logger = logging.getLogger(__name__)


def get_prefix() -> str:
    return f"{configuration.api.api_prefix}/power"


@inject
def get_power_endpoint(
    led_controller_service: LedControllerService = Provide[Container.led_controller_service],
) -> APIRouter:
    router = APIRouter(prefix=get_prefix())

    @router.post("/", status_code=200)
    @translate_service_exceptions
    def toggle_power() -> None:
        logger.debug("Toggling power")
        led_controller_service.toggle_power()
        logger.info("Power successfully toggled")

    return router
