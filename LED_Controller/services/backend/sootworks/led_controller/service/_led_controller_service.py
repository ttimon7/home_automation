import logging
from pathlib import Path
from typing import Iterable

from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.domain.entities import ColorIntensity
from sootworks.led_controller.domain.repository import PwmRepository
from sootworks.led_controller.service._serialization import deserialize_intensities, serialize_intensities

logger = logging.getLogger(__name__)


class LedControllerService:
    def __init__(self, pwm_repository: PwmRepository) -> None:  # noqa: N805
        self.pwm_repository = pwm_repository
        self.intensity_cache_path: Path = configuration.led_controller_service.settings_backup.expanduser()

        self.intensity_cache: Iterable[ColorIntensity] | None = None

    @property
    def saved_intensities(self) -> tuple[ColorIntensity, ...] | None:
        return self._get_saved_intensities()

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

    def toggle_power(self) -> None:
        self.pwm_repository.toggle_power(intensities=self.saved_intensities)

    def apply_intensities(self, intensities: Iterable[ColorIntensity]) -> None:
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
