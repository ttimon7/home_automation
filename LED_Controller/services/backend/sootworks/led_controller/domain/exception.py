"""Domain exceptions."""

import logging
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, NamedTuple, Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Type declarations
ErrorInfo = NamedTuple("ErrorInfo", [("message", str), ("http_status_code", int)])


# Constants
SANITY_RETRY_MARGIN = 100


class LedControllerServiceErrorClass(Enum):
    UNABLE_TO_PERSIST_SETTINGS = ErrorInfo(
        message="Settings could not be saved.",
        http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class LedControllerServiceException(BaseException):
    def __init__(
        self,
        error_class: LedControllerServiceErrorClass,
        error_cause: Optional[BaseException] = None,
    ) -> None:
        self.message = error_class.value.message
        super().__init__(self.message, error_class, error_cause)
        self.error_class = error_class
        self.error_cause = error_cause


def translate_service_exceptions(func: Callable) -> Callable:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except LedControllerServiceException as exc:
            raise HTTPException(
                status_code=exc.error_class.value.http_status_code,
                detail=exc.message,
            ) from exc

    return decorator


def retry(
    func: Callable,
    *args,
    expected_errors: tuple[type[Exception], ...] | None = None,
    limit: int = SANITY_RETRY_MARGIN,
    timeout: float = 0.05,
    **kwargs,
) -> Any:
    # TODO make this async
    expected_errors = expected_errors if isinstance(expected_errors, tuple) else Exception
    counter = 0
    error_cache = None
    while counter < limit:
        try:
            return func(*args, **kwargs)
        except expected_errors as e:
            counter += 1
            error_cache = e
            messaage = f"An error occurred while executing {func.__name__}. The error was: {e}. Attempting a retry"
            logger.warning(messaage)
            time.sleep(timeout)

    message = f"Retry limit exceeded while executing {func.__name__}"
    raise RuntimeError(message) from error_cache
