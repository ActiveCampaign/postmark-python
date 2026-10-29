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

    def test_error_code_numeric_string_coerced_to_int(self):
        response = self._mock_response({"Message": "Bad", "ErrorCode": "300"})
        message, code = parse_error_response(response)
        assert message == "Bad"
        assert code == 300

    def test_error_code_invalid_string_returns_none(self):
        response = self._mock_response({"Message": "Bad", "ErrorCode": "not-a-code"})
        message, code = parse_error_response(response)
        assert message == "Bad"
        assert code is None

    def test_error_code_bool_returns_none(self):
        response = self._mock_response({"Message": "Bad", "ErrorCode": True})
        message, code = parse_error_response(response)
        assert message == "Bad"
        assert code is None

    def test_missing_message_returns_unknown(self):
        response = self._mock_response({"ErrorCode": 422})
        message, code = parse_error_response(response)
        assert message == "Unknown error"
        assert code == 422

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


class TestErrorCodeEdgeCases:
    def _response(self, error_code):
        response = MagicMock()
        response.status_code = 422
        response.text = ""
        response.json.return_value = {"Message": "Bad", "ErrorCode": error_code}
        return response

    def test_blank_string_error_code_returns_none(self):
        for blank in ("", "   "):
            _, code = parse_error_response(self._response(blank))
            assert code is None

    def test_non_integer_types_return_none(self):
        for odd in (12.5, [1], {"code": 1}):
            _, code = parse_error_response(self._response(odd))
            assert code is None

    def test_padded_numeric_string_is_stripped_and_parsed(self):
        _, code = parse_error_response(self._response(" 406 "))
        assert code == 406
