from sootworks.led_controller.controller.dto import RgbwColorDTO
from sootworks.led_controller.domain.entities import Color, ColorIntensity

# Constants
EIGHT_BIT_UPPER_BOUND = 0xFF


def from_8_bit_value_to_percentage(value: int) -> float:
    return value / EIGHT_BIT_UPPER_BOUND


def map_rgbw_color_dto_to_intensities(dto: RgbwColorDTO) -> tuple[ColorIntensity, ...]:
    return tuple(
        ColorIntensity(color=color, value=from_8_bit_value_to_percentage(value=getattr(dto, color.value)))
        for color in Color
    )
