"""Shared fixtures for Postmark test suite."""

from unittest.mock import AsyncMock, Mock
import pytest
from httpx import Response
from postmark.models.messages import OutboundManager


def make_response(data: dict | list) -> Mock:
    """Build a fake httpx.Response returning the given data."""
    response = Mock(spec=Response)
    response.json.return_value = data
    response.raise_for_status = Mock()
    return response


class FakeClient:
    """
    Satisfies the HTTPClient protocol without needing a real ServerClient.
    Inject this into any manager under test.
    """

    def __init__(self):
        self.get = AsyncMock()
        self.post = AsyncMock()

    def mock_get_response(self, data: dict | list) -> None:
        self.get.return_value = make_response(data)

    def mock_post_response(self, data: dict | list) -> None:
        self.post.return_value = make_response(data)

    def mock_get_responses(self, *data_list: dict | list) -> None:
        """Set multiple sequential responses for paginated calls."""
        self.get.side_effect = [make_response(d) for d in data_list]


@pytest.fixture
def fake_client():
    return FakeClient()


@pytest.fixture
def outbound(fake_client):
    """Returns (OutboundManager, FakeClient) for use in tests."""
    return OutboundManager(fake_client), fake_client
