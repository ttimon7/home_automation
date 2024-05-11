import logging
from typing import Generator

logger = logging.getLogger(__name__)


def get_data_point_generator(
    steps: int,
    starting_value: float,
    target_value: float = 0.0,
) -> Generator[float, None, None]:
    if steps < 1:
        message = f"steps must be >= 1, {steps} passed"
        raise ValueError(message)

    value_should_change = starting_value != target_value
    step_size = (target_value - starting_value) / steps
    next_value = starting_value
    for i in range(steps):
        if value_should_change:
            increment = (i + 1) * step_size
            next_value = starting_value + increment
            next_value = max(0, min(1, next_value))

        yield next_value
