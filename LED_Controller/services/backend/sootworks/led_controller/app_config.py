"""Application configuration loading and validation module."""
import logging.config
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Type definitions
LedControllerId = str


# Consts
MB_IN_BYTES = 1024**2


# Enums
class Environment(Enum):
    LOCAL = "LOCAL"
    TEST = "TEST"
    PROD = "PROD"


class LogLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


load_dotenv()


class BaseConfiguration(BaseSettings):
    """Base configuration object based on pydantic.BaseSettings"""

    environment: Environment = Environment.LOCAL
    model_config = SettingsConfigDict(
        env_prefix="",  # Environment variable prefix to load.
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class APIConfiguration(BaseSettings):
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000


class LedControllerChannelMapping(BaseSettings):
    red: int = 14
    green: int = 15
    blue: int = 13
    white: int = 12


class LedControllerSettings(BaseSettings):
    channel_mapping: LedControllerChannelMapping = LedControllerChannelMapping()


class Transition(BaseSettings):
    duration_s: float = 0.4
    frame_rate: int = 30


class Animation(BaseSettings):
    linear_transition: Transition = Transition()


class LedControllerServiceConfiguration(BaseSettings):
    settings_backup: Path = Path("~/led_controller_settings.json")
    power_relay_pins: tuple[int, ...] = Field(default_factory=lambda: (22, 23))
    power_on_signal_value: int = 0
    power_on_delay_s: float = 0.5
    animation: Animation = Animation()
    led_frequency_hz: int = 1600
    controller_settings: dict[LedControllerId, LedControllerSettings] = Field(
        default_factory=lambda: {"pca9685": LedControllerSettings()},
    )


class LogConfiguration(BaseSettings):
    log_level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
    file_path: Optional[str] = None
    size_limit_in_bytes: int = 25 * MB_IN_BYTES
    backup_count: int = 3


class ServiceConfiguration(BaseConfiguration):
    api: APIConfiguration = APIConfiguration()
    led_controller_service: LedControllerServiceConfiguration = LedControllerServiceConfiguration()
    log: LogConfiguration = LogConfiguration()


configuration: ServiceConfiguration = ServiceConfiguration()
