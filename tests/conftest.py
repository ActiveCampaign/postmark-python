"""Shared fixtures for Postmark test suite."""

from unittest.mock import AsyncMock, Mock
import pytest
from httpx import Response
from postmark.models.messages import OutboundManager
from postmark.models.bounces import BounceManager


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
        self.put = AsyncMock()

    def mock_get_response(self, data: dict | list) -> None:
        self.get.return_value = make_response(data)

    def mock_post_response(self, data: dict | list) -> None:
        self.post.return_value = make_response(data)

    def mock_put_response(self, data: dict | list) -> None:
        self.put.return_value = make_response(data)

    def mock_get_responses(self, *data_list: dict | list) -> None:
        """Set multiple sequential responses for paginated calls."""
        self.get.side_effect = [make_response(d) for d in data_list]


@pytest.fixture
def fake_client():
    return FakeClient()


@pytest.fixture
def outbound(fake_client):
    return OutboundManager(fake_client), fake_client


@pytest.fixture
def bounces(fake_client):
    return BounceManager(fake_client), fake_client
