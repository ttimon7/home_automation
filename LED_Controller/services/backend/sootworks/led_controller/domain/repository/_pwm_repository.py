import logging
from abc import ABC, abstractmethod
from typing import Iterable

from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.domain.entities import Color, ColorIntensity

logger = logging.getLogger(__name__)


class PwmRepository(ABC):
    @property
    @abstractmethod
    def controller_id(self) -> str:
        """A unique ID based on which the matching LED controller config can be found."""
        raise NotImplementedError

    @property
    @abstractmethod
    def precision(self) -> int:
        """Precision in bits."""
        raise NotImplementedError

    @property
    def duty_cycle_upper_bound(self) -> int:
        return 2**self.precision - 1

    def _get_channel(self, color: Color) -> int:
        channel_mapping = configuration.led_controller_service.controller_settings[self.controller_id].channel_mapping

        return getattr(channel_mapping, color.value)

    def _get_duty_cycle(self, percentage: float) -> int:
        return int(self.duty_cycle_upper_bound * percentage)

    def _get_default_intensities(self) -> tuple[ColorIntensity, ...]:
        # TODO return previously saved values
        return (
            ColorIntensity(color=Color.RED, value=0),
            ColorIntensity(color=Color.GREEN, value=0),
            ColorIntensity(color=Color.BLUE, value=0),
            ColorIntensity(color=Color.WHITE, value=0.2157),
        )

    @abstractmethod
    def _apply_duty_cycle(self, channel: int, duty_cycle: int) -> None:
        raise NotImplementedError

    def _update_power_state(self, duty_cycle: int) -> None:
        if duty_cycle > 0:
            self.powered_on = True

    def set_intensity(self, pair: ColorIntensity) -> None:
        channel = self._get_channel(color=pair.color)
        duty_cycle = self._get_duty_cycle(percentage=pair.value)
        self._apply_duty_cycle(channel=channel, duty_cycle=duty_cycle)
        self._update_power_state(duty_cycle=duty_cycle)

    def toggle_power(self, intensities: Iterable[ColorIntensity] | None) -> None:
        original_power_state = self.powered_on
        logger.debug(f"Current power state: {original_power_state}")
        # NOTE Inverting power state here will not interfere with the adjustment made by set_intensity
        self.powered_on = not original_power_state

        default_intensities = self._get_default_intensities() if intensities is None else intensities
        pairs = (
            (ColorIntensity(color=color, value=0) for color in Color) if original_power_state else default_intensities
        )

        for pair in pairs:
            self.set_intensity(pair=pair)

        logger.debug(f"New power state: {self.powered_on}")
