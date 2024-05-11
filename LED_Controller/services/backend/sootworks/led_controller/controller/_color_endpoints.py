import logging

from dependency_injector.wiring import Provide, inject
from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.containers import Container
from sootworks.led_controller.controller._mappers import map_rgbw_color_dto_to_intensities
from sootworks.led_controller.controller.dto import RgbwColorDTO
from sootworks.led_controller.domain.exception import translate_service_exceptions
from sootworks.led_controller.infrastructure.fast_api_utils import APIRouter
from sootworks.led_controller.service import LedControllerService

logger = logging.getLogger(__name__)


def get_prefix() -> str:
    return f"{configuration.api.api_prefix}/color"


@inject
def get_color_endpoints(
    led_controller_service: LedControllerService = Provide[Container.led_controller_service],
) -> APIRouter:
    router = APIRouter(prefix=get_prefix())

    @router.post("/", status_code=200)
    @translate_service_exceptions
    def set_colors(request: RgbwColorDTO) -> RgbwColorDTO:
        logger.debug(f"Setting color values {request}")
        intensities = map_rgbw_color_dto_to_intensities(dto=request)
        logger.debug(f"Values translated to intensities ({intensities})")
        led_controller_service.apply_intensities(intensities=intensities)
        logger.info("Values successfully set")

        return request

    @router.post("/save", status_code=200)
    @translate_service_exceptions
    def save_state() -> None:
        logger.debug("Saving state")
        success = led_controller_service.save_intensities()
        logger.info("State successfully saved" if success else "Failed to save state")

    return router
