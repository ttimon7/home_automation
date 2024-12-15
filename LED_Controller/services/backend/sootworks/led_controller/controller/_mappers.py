from typing import Callable
from sootworks.led_controller.app_config import configuration
from sootworks.led_controller.controller.dto import RgbwColorDTO
from sootworks.led_controller.domain.entities import Color, ColorIntensity, InputScale

# Constants
BASE = 1.049
Y_MATCHING_FULL_INTENSITY = 10
X_MATCHING_FULL_INTENSITY = 50
EIGHT_BIT_UPPER_BOUND = 0xFF


def _from_8_bit_value_to_percentage_linear_scale(value: int) -> float:
    return value / EIGHT_BIT_UPPER_BOUND


def _from_8_bit_value_to_percentage_exponential_scale(value: int) -> float:
    intensity = 1.0
    if value < EIGHT_BIT_UPPER_BOUND:
        linear_percentage = _from_8_bit_value_to_percentage_linear_scale(value=value)
        scaled_x = X_MATCHING_FULL_INTENSITY * linear_percentage
        intensity = (BASE**scaled_x - 1) / Y_MATCHING_FULL_INTENSITY

    return intensity


def _get_scaling_method() -> Callable[[int], float]:
    method = None
    match configuration.api.input_scale:
        case InputScale.LINEAR:
            method = _from_8_bit_value_to_percentage_linear_scale
        case InputScale.EXPONENTIAL:
            method = _from_8_bit_value_to_percentage_exponential_scale
        case _:
            message = f"Unknown scaling method requested: {configuration.api.input_scale}"
            raise ValueError(message)

    return method


def map_rgbw_color_dto_to_intensities(dto: RgbwColorDTO) -> tuple[ColorIntensity, ...]:
    scaling_method = _get_scaling_method()
    return tuple(ColorIntensity(color=color, value=scaling_method(value=getattr(dto, color.value))) for color in Color)
