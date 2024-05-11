import json
import logging
from typing import Iterable

from sootworks.led_controller.domain.entities import ColorIntensity

logger = logging.getLogger(__name__)


def serialize_intensities(intensities: Iterable[ColorIntensity]) -> str | None:
    prepared = []
    for pair in intensities:
        prepared.append(pair.model_dump_json())

    if prepared is None:
        logger.warning(f"Failed to serialize intesity values: {intensities}")
    else:
        logger.debug(f"Successfully serialize intesity values: {prepared}")

    return None if len(prepared) == 0 else "[" + ",".join(prepared) + "]"


def deserialize_intensities(serialized: str) -> tuple[ColorIntensity, ...] | None:
    intensities = None

    try:
        intensities = tuple(ColorIntensity(**v) for v in json.loads(serialized))
        logger.debug(f"Successfully deserialize intesity values: {intensities}")
    except Exception as e:  # noqa: BLE001, NOTE intentional, no error raised here is critical
        logger.warning(f"Failed to deserialize intesity values. The error was: {e}")

    return intensities
