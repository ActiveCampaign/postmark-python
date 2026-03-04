"""Shared fixtures for Postmark test suite."""

from unittest.mock import AsyncMock, Mock

import pytest
from httpx import Response

from postmark.models.bounces import BounceManager
from postmark.models.data_removals import DataRemovalManager
from postmark.models.domains import DomainManager
from postmark.models.inbound import InboundManager
from postmark.models.inbound_rules import InboundRuleManager
from postmark.models.messages import OutboundManager
from postmark.models.servers import AccountServerManager, ServerManager
from postmark.models.signatures import SenderSignatureManager
from postmark.models.stats import StatsManager
from postmark.models.streams import StreamManager
from postmark.models.suppressions import SuppressionManager
from postmark.models.templates import TemplateManager
from postmark.models.webhooks import WebhookManager


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
        self.patch = AsyncMock()
        self.delete = AsyncMock()

    def mock_get_response(self, data: dict | list) -> None:
        self.get.return_value = make_response(data)

    def mock_post_response(self, data: dict | list) -> None:
        self.post.return_value = make_response(data)

    def mock_put_response(self, data: dict | list) -> None:
        self.put.return_value = make_response(data)

    def mock_patch_response(self, data: dict | list) -> None:
        self.patch.return_value = make_response(data)

    def mock_delete_response(self, data: dict | list) -> None:
        self.delete.return_value = make_response(data)

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


@pytest.fixture
def templates(fake_client):
    return TemplateManager(fake_client), fake_client


@pytest.fixture
def servers(fake_client):
    return ServerManager(fake_client), fake_client


@pytest.fixture
def account_servers(fake_client):
    return AccountServerManager(fake_client), fake_client


@pytest.fixture
def streams(fake_client):
    return StreamManager(fake_client), fake_client


@pytest.fixture
def inbound(fake_client):
    return InboundManager(fake_client), fake_client


@pytest.fixture
def domains(fake_client):
    return DomainManager(fake_client), fake_client


@pytest.fixture
def signatures(fake_client):
    return SenderSignatureManager(fake_client), fake_client


@pytest.fixture
def stats(fake_client):
    return StatsManager(fake_client), fake_client


@pytest.fixture
def inbound_rules(fake_client):
    return InboundRuleManager(fake_client), fake_client


@pytest.fixture
def webhooks(fake_client):
    return WebhookManager(fake_client), fake_client


@pytest.fixture
def suppressions(fake_client):
    return SuppressionManager(fake_client), fake_client


@pytest.fixture
def data_removals(fake_client):
    return DataRemovalManager(fake_client), fake_client
