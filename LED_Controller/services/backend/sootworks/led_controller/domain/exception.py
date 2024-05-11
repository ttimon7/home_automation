"""Domain exceptions."""

from enum import Enum
from functools import wraps
from typing import Any, Callable, NamedTuple, Optional

from fastapi import HTTPException, status

# Type declarations
ErrorInfo = NamedTuple("ErrorInfo", [("message", str), ("http_status_code", int)])


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
