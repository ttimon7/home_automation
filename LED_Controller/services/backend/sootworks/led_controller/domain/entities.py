from enum import Enum

from pydantic import BaseModel


# Enums
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    WHITE = "white"


# Models
class ColorIntensity(BaseModel):
    color: Color
    value: float
