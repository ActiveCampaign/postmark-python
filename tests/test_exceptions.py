"""Tests for Postmark exception helpers."""

import pytest

from postmark.exceptions import (
    InactiveRecipientException,
    InvalidAPIKeyException,
    PostmarkAPIException,
    RateLimitException,
    ServerException,
    ValidationException,
)


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (
            "Found inactive addresses: john@example.com. Emails to these addresses "
            "are not accepted or delivered by Postmark.",
            ["john@example.com"],
        ),
        (
            "Found inactive addresses: john@example.com, jane@test.org. Emails to "
            "these addresses are not accepted or delivered by Postmark.",
            ["john@example.com", "jane@test.org"],
        ),
        (
            "Found inactive addresses: a@example.co, b@example.io, c@example.net.",
            ["a@example.co", "b@example.io", "c@example.net"],
        ),
        (
            "Found inactive addresses:john@example.com.",
            ["john@example.com"],
        ),
        (
            "Inactive recipient.",
            [],
        ),
    ],
)
def test_inactive_recipient_exception_parses_inactive_recipients(
    message: str, expected: list[str]
):
    exc = InactiveRecipientException(message, error_code=406, http_status=406)

    assert exc.inactive_recipients == expected


class TestGetExceptionClassHttpFallbacks:
    """With no (or an unknown) Postmark error code, the HTTP status decides."""

    @pytest.mark.parametrize(
        "http_status,expected",
        [
            (401, InvalidAPIKeyException),
            (422, ValidationException),
            (429, RateLimitException),
            (500, ServerException),
            (503, ServerException),
            (404, PostmarkAPIException),
            (418, PostmarkAPIException),
        ],
    )
    @pytest.mark.parametrize("error_code", [0, 99999])
    def test_status_fallback(self, http_status, expected, error_code):
        from postmark.exceptions import get_exception_class

        assert get_exception_class(error_code, http_status) is expected

    def test_known_error_code_wins_over_http_status(self):
        from postmark.exceptions import get_exception_class

        # 406 is an inactive-recipient error even when the HTTP status says 422
        assert get_exception_class(406, 422) is not ValidationException
