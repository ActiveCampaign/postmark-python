"""Tests for Postmark exception helpers."""

import pytest

from postmark.exceptions import InactiveRecipientException


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
