"""Postmark API exceptions."""

from typing import Any, Dict, Optional


class PostmarkException(Exception):
    """Base exception for all Postmark errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[int] = None,
        http_status: Optional[int] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.http_status = http_status
        self.message = message


class PostmarkAPIException(PostmarkException):
    """API errors with error codes from Postmark."""

    def __init__(self, message: str, error_code: int, http_status: int):
        super().__init__(message, error_code, http_status)

    def __str__(self):
        return f"[{self.error_code}] {self.message} (HTTP {self.http_status})"


# Specific exception types for common errors
class InvalidAPIKeyException(PostmarkAPIException):
    """401 - Invalid or missing API key."""

    pass


class InactiveRecipientException(PostmarkAPIException):
    """406 - Inactive recipient."""

    pass


class ValidationException(PostmarkAPIException):
    """422 - Invalid request parameters."""

    pass


class RateLimitException(PostmarkAPIException):
    """429 - Rate limit exceeded."""

    pass


class ServerException(PostmarkAPIException):
    """500/503 - Server errors."""

    pass


class TimeoutException(PostmarkException):
    """Request timeout."""

    pass


# Error code mapping
ERROR_CODE_MAPPING = {
    10: InvalidAPIKeyException,
    406: InactiveRecipientException,
    300: ValidationException,
    405: ValidationException,  # Not allowed to send
    701: ValidationException,  # Illegal attachment type
    429: RateLimitException,
    500: ServerException,
    503: ServerException,
}


def get_exception_class(
    error_code: int, http_status: int
) -> type[PostmarkAPIException]:
    """Get the appropriate exception class for an error code."""
    # Check specific error codes first
    if error_code in ERROR_CODE_MAPPING:
        return ERROR_CODE_MAPPING[error_code]

    # Fall back to HTTP status
    if http_status == 401:
        return InvalidAPIKeyException
    elif http_status == 422:
        return ValidationException
    elif http_status == 429:
        return RateLimitException
    elif http_status in (500, 503):
        return ServerException

    return PostmarkAPIException
