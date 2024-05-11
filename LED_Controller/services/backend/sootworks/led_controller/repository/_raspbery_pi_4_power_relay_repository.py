import logging

from sootworks.led_controller.app_config import Environment, configuration
from sootworks.led_controller.domain.entities import PowerState
from sootworks.led_controller.domain.repository import PowerRelayRepository

# TODO this is not the nicest solution come up with something better
if configuration.environment in {Environment.TEST, Environment.PROD}:
    from RPi import GPIO
else:
    from unittest.mock import MagicMock

    state = 1

    def mock_state_switching(_channel: int, _value: int):  # noqa: ANN202
        global state  # noqa: PLW0603

        state = _value

        return state

    GPIO = MagicMock()
    GPIO.input = lambda *_, **__: state
    GPIO.output = mock_state_switching

logger = logging.getLogger(__name__)


class RP4PowerRelayRepository(PowerRelayRepository):
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BCM)
        for pin_number in configuration.led_controller_service.power_relay_pins:
            GPIO.setup(pin_number, GPIO.OUT)
            GPIO.output(pin_number, self.power_off_signal)

    @property
    def powered_on(self) -> bool:
        # It's enough to measure one, as they are controlled together
        pin_number = configuration.led_controller_service.power_relay_pins[0]
        power_on_signal_value = configuration.led_controller_service.power_on_signal_value
        pin_state = GPIO.input(pin_number)
        is_powered_on = pin_state == power_on_signal_value
        logger.debug(f"Device is powered {'ON' if is_powered_on else 'OFF'} (pin_state: {pin_state})")

        return is_powered_on

    def toggle_power(self) -> PowerState:
        original_power_state = self.powered_on
        logger.debug(f"Trying to turn device {'OFF' if original_power_state else 'ON'}")

        value = self.power_off_signal if original_power_state else self.power_on_signal
        for pin_number in configuration.led_controller_service.power_relay_pins:
            logger.debug(f"Setting pin {pin_number} to {value}")
            GPIO.output(pin_number, value)

        logger.info(f"Successfully turned device {self.power_state.name}")

        return self.power_state

    def cleanup() -> None:
        GPIO.cleanup()
