"""Tests for postmark.utils.server_utils."""

from unittest.mock import MagicMock

from postmark.utils.server_utils import parse_error_response


class TestParseErrorResponse:
    def _mock_response(self, json_data=None, text="", status_code=200, raise_json=None):
        response = MagicMock()
        response.status_code = status_code
        response.text = text
        if raise_json is not None:
            response.json.side_effect = raise_json
        else:
            response.json.return_value = json_data
        return response

    # --- Happy path ---

    def test_returns_message_and_error_code(self):
        response = self._mock_response({"Message": "Bad token", "ErrorCode": 401})
        message, code = parse_error_response(response)
        assert message == "Bad token"
        assert code == 401

    def test_missing_error_code_returns_none(self):
        response = self._mock_response({"Message": "Oops"})
        message, code = parse_error_response(response)
        assert message == "Oops"
        assert code is None

    def test_missing_message_returns_unknown(self):
        response = self._mock_response({"ErrorCode": 422})
        message, code = parse_error_response(response)
        assert message == "Unknown error"
        assert code == 422

    # --- Except branch (lines 14-16) ---

    def test_json_decode_error_falls_back_to_text(self):
        import json

        response = self._mock_response(
            raise_json=json.JSONDecodeError("msg", "", 0),
            text="Bad gateway",
            status_code=502,
        )
        message, code = parse_error_response(response)
        assert message == "Bad gateway"
        assert code is None

    def test_json_decode_error_empty_text_falls_back_to_status(self):
        import json

        response = self._mock_response(
            raise_json=json.JSONDecodeError("msg", "", 0), text="", status_code=503
        )
        message, code = parse_error_response(response)
        assert message == "HTTP 503 error"
        assert code is None

    def test_attribute_error_falls_back_to_text(self):
        response = self._mock_response(
            raise_json=AttributeError("no json"), text="Internal error", status_code=500
        )
        message, code = parse_error_response(response)
        assert message == "Internal error"
        assert code is None

    def test_attribute_error_empty_text_falls_back_to_status(self):
        response = self._mock_response(
            raise_json=AttributeError("no json"), text="", status_code=500
        )
        message, code = parse_error_response(response)
        assert message == "HTTP 500 error"
        assert code is None
