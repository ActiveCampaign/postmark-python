"""Tests for postmark.utils.message_utils."""

import pytest

from postmark.utils.message_utils import validate_email_list, validate_formatted_email


class TestValidateFormattedEmail:
    def test_none_raises(self):
        with pytest.raises(ValueError, match="Email cannot be None"):
            validate_formatted_email(None)

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Email cannot be empty"):
            validate_formatted_email("")

    def test_no_email_pattern_raises(self):
        with pytest.raises(ValueError, match="Invalid email field format"):
            validate_formatted_email("not-an-email")

    def test_invalid_email_in_angle_brackets_raises(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            validate_formatted_email("Name <notvalid>")

    def test_valid_plain_email(self):
        assert validate_formatted_email("user@example.com") == "user@example.com"

    def test_valid_formatted_email(self):
        v = '"Alice" <alice@example.com>'
        assert validate_formatted_email(v) == v


class TestValidateEmailList:
    def test_invalid_email_raises(self):
        with pytest.raises(ValueError, match="Invalid email address in list"):
            validate_email_list(["good@example.com", "notvalid"])

    def test_valid_list(self):
        emails = ["a@example.com", "b@example.com"]
        assert validate_email_list(emails) == emails

    def test_empty_list(self):
        assert validate_email_list([]) == []
