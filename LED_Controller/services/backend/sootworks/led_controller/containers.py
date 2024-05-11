from dependency_injector import containers, providers
from sootworks.led_controller.repository import PCA9685PwmRepository
from sootworks.led_controller.service import LedControllerService


class Container(containers.DeclarativeContainer):
    # Depencency injection requires wiring between containers and their target modules
    wiring_config = containers.WiringConfiguration(
        modules=[
            "sootworks.led_controller.controller._color_endpoints",
            "sootworks.led_controller.controller._power_endpoint",
        ],
    )

    # Repositories
    pwm_repository = providers.Singleton(PCA9685PwmRepository)

    # Services
    led_controller_service = providers.Singleton(
        LedControllerService,
        pwm_repository=pwm_repository,
    )
