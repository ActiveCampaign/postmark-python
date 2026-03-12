"""Postmark API exceptions."""

import re
from typing import Any, Optional


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

    @property
    def message(self) -> str:
        """The error message. Alias for self.args[0]."""
        return self.args[0]


class InvalidEmailException(PostmarkException):
    """
    Raised when an email dict or model fails Pydantic validation
    before it is ever sent to the API.

    Distinct from ValidationException, which maps to HTTP 422 responses
    from the Postmark API after a request was made.
    """

    def __init__(self, errors: list[Any]):
        self.errors = errors
        summary = " | ".join(
            f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors
        )
        super().__init__(f"Invalid email: {summary}")


class PostmarkAPIException(PostmarkException):
    """
    Raised for errors returned by the Postmark API.
    Always carries both a Postmark error_code and an http_status.
    """

    def __init__(
        self,
        message: str,
        error_code: int,
        http_status: int,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, error_code, http_status)
        self.request_id = request_id

    def __str__(self):
        base = f"[{self.error_code}] {self.message} (HTTP {self.http_status})"
        return f"{base} [request_id={self.request_id}]" if self.request_id else base


class InvalidAPIKeyException(PostmarkAPIException):
    """401 - Invalid or missing API key."""

    pass


class InactiveRecipientException(PostmarkAPIException):
    """406 - Inactive recipient."""

    def __init__(
        self,
        message: str,
        error_code: int,
        http_status: int,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, error_code, http_status, request_id)
        match = re.search(r"Found inactive addresses: ([^.]+)", message)
        self.inactive_recipients: list[str] = (
            [a for addr in match.group(1).split(",") if (a := addr.strip())]
            if match
            else []
        )


class ValidationException(PostmarkAPIException):
    """422 - Invalid request parameters (rejected by Postmark API)."""

    pass


class RateLimitException(PostmarkAPIException):
    """429 - Rate limit exceeded."""

    pass


class ServerException(PostmarkAPIException):
    """500 / 503 - Server-side error."""

    pass


class TimeoutException(PostmarkException):
    """Raised when a request to the Postmark API times out."""

    pass


# Postmark API error codes (from response body), not HTTP status codes.
# See: https://postmarkapp.com/developer/api/overview#error-codes
_ERROR_CODE_MAP: dict[int, type[PostmarkAPIException]] = {
    10: InvalidAPIKeyException,
    300: ValidationException,
    405: ValidationException,  # Not allowed to send
    406: InactiveRecipientException,
    701: ValidationException,  # Illegal attachment type
}


def get_exception_class(
    error_code: int, http_status: int
) -> type[PostmarkAPIException]:
    """
    Resolve the most specific exception class for a failed API response.

    Checks Postmark error codes first (more specific), then falls back
    to HTTP status codes, and finally to the generic PostmarkAPIException.
    """
    if error_code in _ERROR_CODE_MAP:
        return _ERROR_CODE_MAP[error_code]

    if http_status == 401:
        return InvalidAPIKeyException
    if http_status == 422:
        return ValidationException
    if http_status == 429:
        return RateLimitException
    if http_status in (500, 503):
        return ServerException

    return PostmarkAPIException
