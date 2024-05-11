from abc import ABC, abstractmethod

from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.domain.entities import PowerState


class PowerRelayRepository(ABC):
    @property
    @abstractmethod
    def powered_on(self) -> bool:
        raise NotImplementedError

    @property
    def power_state(self) -> PowerState:
        return PowerState.ON if self.powered_on else PowerState.OFF

    @property
    def power_on_signal(self) -> int:
        return configuration.led_controller_service.power_on_signal_value

    @property
    def power_off_signal(self) -> int:
        return int(not bool(self.power_on_signal))

    def turn_on_device(self) -> None:
        if not self.powered_on:
            self.toggle_power()

    @abstractmethod
    def toggle_power(self) -> PowerState:
        """Toggle the power state of the main power supply."""
        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError
