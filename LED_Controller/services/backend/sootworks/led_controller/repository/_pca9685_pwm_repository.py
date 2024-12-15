import logging

import board
from adafruit_pca9685 import PCA9685
from sootworks.led_controller.app_config import Environment, configuration
from sootworks.led_controller.domain.exception import retry
from sootworks.led_controller.domain.repository import PwmRepository

logger = logging.getLogger(__name__)


class PCA9685PwmRepository(PwmRepository):
    def __init__(self) -> None:
        # The board.I2C() call will fail on PC, as it has no I2C interface.
        #
        # TODO this is far from being ideal, find a better solution
        if configuration.environment is not Environment.LOCAL:
            # Create the I2C bus interface.
            self.i2c = board.I2C()  # uses board.SCL and board.SDA
            # Create a simple PCA9685 class instance.
            self.pca = PCA9685(self.i2c)
            # Set the PWM frequency [Hz].
            self.pca.frequency = configuration.led_controller_service.led_frequency_hz

    @property
    def controller_id(self) -> str:
        return "pca9685"

    @property
    def precision(self) -> int:
        """Precision in bits.

        The duty cycle used by the adafruit_pca9685 library is 16 bits to match other PWM objects
        but the PCA9685 will only actually give 12 bits of resolution.
        """
        return 16

    def _apply_duty_cycle(self, channel: int, duty_cycle: int) -> None:
        logger.info(f"Applying duty cycle ({duty_cycle}) to channel ({channel}).")

        if configuration.environment is not Environment.LOCAL:

            def _apply() -> None:
                self.pca.channels[channel].duty_cycle = duty_cycle

            retry(func=_apply, expected_errors=(OSError,))
