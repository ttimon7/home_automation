import logging
from abc import ABC, abstractmethod

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

    @abstractmethod
    def _apply_duty_cycle(self, channel: int, duty_cycle: int) -> None:
        raise NotImplementedError

    def set_intensity(self, pair: ColorIntensity) -> None:
        channel = self._get_channel(color=pair.color)
        duty_cycle = self._get_duty_cycle(percentage=pair.value)
        self._apply_duty_cycle(channel=channel, duty_cycle=duty_cycle)
