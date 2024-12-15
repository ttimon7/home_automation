import logging
import time
from pathlib import Path
from typing import Iterable

from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.domain.entities import Color, ColorIntensity, PowerState
from sootworks.led_controller.domain.repository import PowerRelayRepository, PwmRepository
from sootworks.led_controller.service._animation import get_data_point_generator
from sootworks.led_controller.service._serialization import deserialize_intensities, serialize_intensities

logger = logging.getLogger(__name__)


class LedControllerService:
    DEFAULT_INTENSITIES: tuple[ColorIntensity, ...] = (
        ColorIntensity(color=Color.RED, value=0),
        ColorIntensity(color=Color.GREEN, value=0),
        ColorIntensity(color=Color.BLUE, value=0),
        ColorIntensity(color=Color.WHITE, value=0.2157),
    )

    def __init__(self, power_relay_repository: PowerRelayRepository, pwm_repository: PwmRepository) -> None:  # noqa: N805
        self.power_relay_repository = power_relay_repository
        self.pwm_repository = pwm_repository
        self.intensity_cache_path: Path = configuration.led_controller_service.settings_backup.expanduser()

        self.intensity_cache: Iterable[ColorIntensity] | None = None

        self.lock = False

    @property
    def saved_intensities(self) -> tuple[ColorIntensity, ...]:
        recalled_intensities = self._get_saved_intensities()
        return self.DEFAULT_INTENSITIES if recalled_intensities is None else recalled_intensities

    def _get_saved_intensities(self) -> tuple[ColorIntensity, ...] | None:
        intensities = None

        if self.intensity_cache_path.is_file():
            try:
                serialized = self.intensity_cache_path.read_text()
                logger.debug(f"Serialized values read: {serialized}")
                intensities = deserialize_intensities(serialized=serialized)
            except Exception as e:  # noqa: BLE001, NOTE intentional, no error raised here is critical
                logger.warning(f"Unable to load cached intensity values. The error was: {e}")

        return intensities

    def _animate_lights(
        self,
        steps: int,
        generators: dict[Color, float],
        should_sleep_seconds: float,
    ) -> None:
        for i in range(steps):
            logger.debug(f"Applying light transition ({i})")
            for color, generator in generators.items():
                new_pair = ColorIntensity(color=color, value=next(generator))

                logger.debug(f"Setting {new_pair.color.name}: to {new_pair.value}")

                self.pwm_repository.set_intensity(pair=new_pair)

            time.sleep(should_sleep_seconds)

    def _animate_lights_linear(
        self,
        fade_in: bool,
        intensities: tuple[ColorIntensity, ...],
    ) -> None:
        # TODO make it more generic should the need for more animations arise
        self.lock = True

        duration = configuration.led_controller_service.animation.linear_transition.duration_s
        steps = int(duration * configuration.led_controller_service.animation.linear_transition.frame_rate)
        should_sleep_seconds = duration / steps
        generators = {
            pair.color: get_data_point_generator(
                steps=steps,
                starting_value=(0 if fade_in else pair.value),
                target_value=(pair.value if fade_in else 0),
            )
            for pair in intensities
        }
        self._animate_lights(steps=steps, generators=generators, should_sleep_seconds=should_sleep_seconds)

        self.lock = False

    def toggle_power(self) -> None:
        if self.power_relay_repository.power_state is PowerState.ON:
            self._animate_lights_linear(fade_in=False, intensities=self.intensity_cache)

        power_state = self.power_relay_repository.toggle_power()

        if power_state is PowerState.ON:
            time.sleep(
                configuration.led_controller_service.power_on_delay_s,  # Waiting for the PSU to properly energize
            )
            intensities = self.DEFAULT_INTENSITIES if self.saved_intensities is None else self.saved_intensities
            self.intensity_cache = intensities
            self._animate_lights_linear(fade_in=True, intensities=intensities)

    def apply_intensities(self, intensities: Iterable[ColorIntensity]) -> None:
        if self.lock:
            return

        for pair in intensities:
            self.pwm_repository.set_intensity(pair=pair)

        self.intensity_cache = intensities

    def save_intensities(self, intensities: Iterable[ColorIntensity] | None = None) -> bool:
        """Return `True` if the intesities were successfully saved and `False` if there was nothing to persist."""
        success = False
        selected = self.intensity_cache if intensities is None else intensities
        if selected is not None:
            serialized = serialize_intensities(intensities=selected)
            if serialized is not None:
                self.intensity_cache_path.write_text(serialized)
                success = True

        return success
