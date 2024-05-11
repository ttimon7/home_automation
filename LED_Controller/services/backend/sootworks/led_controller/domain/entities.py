from enum import Enum

from pydantic import BaseModel


# Enums
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    WHITE = "white"


class PowerState(Enum):
    ON = "on"
    OFF = "off"


# Models
class ColorIntensity(BaseModel):
    color: Color
    value: float  # [%], [0.0, 1.0]
