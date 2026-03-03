"""Tests for the AccountServerManager."""

import pytest

from postmark.models.servers import DeliveryType, ServerColor, TrackLinks

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

SERVER = {
    "ID": 42,
    "Name": "Test Server",
    "ApiTokens": ["token-abc"],
    "Color": "Blue",
    "SmtpApiActivated": True,
    "RawEmailEnabled": False,
    "DeliveryType": "Live",
    "ServerLink": "https://account.postmarkapp.com/servers/42/streams",
    "InboundAddress": "abc@inbound.postmarkapp.com",
    "InboundHookUrl": None,
    "BounceHookUrl": None,
    "OpenHookUrl": None,
    "DeliveryHookUrl": None,
    "PostFirstOpenOnly": False,
    "InboundDomain": None,
    "InboundHash": "abc",
    "InboundSpamThreshold": 5,
    "TrackOpens": False,
    "TrackLinks": "None",
    "IncludeBounceContentInHook": False,
    "ClickHookUrl": None,
    "EnableSmtpApiErrorHooks": False,
}


def _make_server(**overrides) -> dict:
    return {**SERVER, **overrides}


# ---------------------------------------------------------------------------
# Get server
# ---------------------------------------------------------------------------


class TestGetServer:
    @pytest.mark.asyncio
    async def test_get_success(self, account_servers):
        manager, fake = account_servers
        fake.mock_get_response(SERVER)

        server = await manager.get(42)

        assert server.id == 42
        assert server.name == "Test Server"
        assert server.color == ServerColor.BLUE

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, account_servers):
        manager, fake = account_servers
        fake.mock_get_response(SERVER)

        await manager.get(42)

        fake.get.assert_called_once_with("/servers/42")

    @pytest.mark.asyncio
    async def test_get_different_server_id(self, account_servers):
        manager, fake = account_servers
        fake.mock_get_response(_make_server(ID=999))

        await manager.get(999)

        fake.get.assert_called_once_with("/servers/999")


# ---------------------------------------------------------------------------
# Create server
# ---------------------------------------------------------------------------


class TestCreateServer:
    @pytest.mark.asyncio
    async def test_create_name_only(self, account_servers):
        manager, fake = account_servers
        fake.mock_post_response(_make_server(Name="New Server"))

        server = await manager.create(name="New Server")

        assert server.name == "New Server"
        fake.post.assert_called_once_with("/servers", json={"Name": "New Server"})

    @pytest.mark.asyncio
    async def test_create_with_optional_fields(self, account_servers):
        manager, fake = account_servers
        fake.mock_post_response(
            _make_server(
                Name="Sandbox Server",
                DeliveryType="Sandbox",
                Color="Green",
                TrackOpens=True,
            )
        )

        server = await manager.create(
            name="Sandbox Server",
            delivery_type=DeliveryType.SANDBOX,
            color=ServerColor.GREEN,
            track_opens=True,
        )

        assert server.delivery_type == DeliveryType.SANDBOX
        assert server.color == ServerColor.GREEN
        body = fake.post.call_args[1]["json"]
        assert body["Name"] == "Sandbox Server"
        assert body["DeliveryType"] == "Sandbox"
        assert body["Color"] == "Green"
        assert body["TrackOpens"] is True

    @pytest.mark.asyncio
    async def test_create_with_webhook_urls(self, account_servers):
        manager, fake = account_servers
        fake.mock_post_response(SERVER)

        await manager.create(
            name="Test",
            inbound_hook_url="https://example.com/inbound",
            bounce_hook_url="https://example.com/bounce",
        )

        body = fake.post.call_args[1]["json"]
        assert body["InboundHookUrl"] == "https://example.com/inbound"
        assert body["BounceHookUrl"] == "https://example.com/bounce"

    @pytest.mark.asyncio
    async def test_create_with_track_links(self, account_servers):
        manager, fake = account_servers
        fake.mock_post_response(SERVER)

        await manager.create(name="Test", track_links=TrackLinks.HTML_ONLY)

        body = fake.post.call_args[1]["json"]
        assert body["TrackLinks"] == "HtmlOnly"


# ---------------------------------------------------------------------------
# Edit server
# ---------------------------------------------------------------------------


class TestEditServer:
    @pytest.mark.asyncio
    async def test_edit_name(self, account_servers):
        manager, fake = account_servers
        fake.mock_put_response(_make_server(Name="Renamed"))

        server = await manager.edit(42, name="Renamed")

        assert server.name == "Renamed"
        fake.put.assert_called_once_with("/servers/42", json={"Name": "Renamed"})

    @pytest.mark.asyncio
    async def test_edit_calls_correct_endpoint(self, account_servers):
        manager, fake = account_servers
        fake.mock_put_response(SERVER)

        await manager.edit(99, name="X")

        fake.put.assert_called_once_with("/servers/99", json={"Name": "X"})

    @pytest.mark.asyncio
    async def test_edit_no_args_sends_empty_body(self, account_servers):
        manager, fake = account_servers
        fake.mock_put_response(SERVER)

        await manager.edit(42)

        fake.put.assert_called_once_with("/servers/42", json={})

    @pytest.mark.asyncio
    async def test_edit_multiple_fields(self, account_servers):
        manager, fake = account_servers
        fake.mock_put_response(SERVER)

        await manager.edit(
            42,
            color=ServerColor.RED,
            track_opens=True,
            inbound_spam_threshold=10,
        )

        body = fake.put.call_args[1]["json"]
        assert body == {
            "Color": "Red",
            "TrackOpens": True,
            "InboundSpamThreshold": 10,
        }


# ---------------------------------------------------------------------------
# List servers
# ---------------------------------------------------------------------------


class TestListServers:
    @pytest.fixture
    def list_response(self):
        return {
            "TotalCount": 2,
            "Servers": [
                _make_server(ID=1, Name="Alpha"),
                _make_server(ID=2, Name="Beta"),
            ],
        }

    @pytest.mark.asyncio
    async def test_list_success(self, account_servers, list_response):
        manager, fake = account_servers
        fake.mock_get_response(list_response)

        servers, total = await manager.list()

        assert total == 2
        assert len(servers) == 2
        assert servers[0].name == "Alpha"
        assert servers[1].name == "Beta"

    @pytest.mark.asyncio
    async def test_list_default_params(self, account_servers):
        manager, fake = account_servers
        fake.mock_get_response({"TotalCount": 0, "Servers": []})

        await manager.list()

        fake.get.assert_called_once_with("/servers", params={"count": 100, "offset": 0})

    @pytest.mark.asyncio
    async def test_list_with_name_filter(self, account_servers):
        manager, fake = account_servers
        fake.mock_get_response({"TotalCount": 0, "Servers": []})

        await manager.list(name="staging")

        params = fake.get.call_args[1]["params"]
        assert params["name"] == "staging"

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, account_servers):
        manager, fake = account_servers
        fake.mock_get_response({"TotalCount": 0, "Servers": []})

        await manager.list(count=10, offset=20)

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 10
        assert params["offset"] == 20

    @pytest.mark.asyncio
    async def test_list_empty(self, account_servers):
        manager, fake = account_servers
        fake.mock_get_response({"TotalCount": 0, "Servers": []})

        servers, total = await manager.list()

        assert total == 0
        assert servers == []


# ---------------------------------------------------------------------------
# Delete server
# ---------------------------------------------------------------------------


class TestDeleteServer:
    @pytest.mark.asyncio
    async def test_delete_success(self, account_servers):
        manager, fake = account_servers
        fake.mock_delete_response({"ErrorCode": 0, "Message": "Server removed."})

        result = await manager.delete(42)

        assert result.error_code == 0
        assert result.message == "Server removed."

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self, account_servers):
        manager, fake = account_servers
        fake.mock_delete_response({"ErrorCode": 0, "Message": "Server removed."})

        await manager.delete(42)

        fake.delete.assert_called_once_with("/servers/42")

    @pytest.mark.asyncio
    async def test_delete_does_not_call_other_methods(self, account_servers):
        manager, fake = account_servers
        fake.mock_delete_response({"ErrorCode": 0, "Message": "Server removed."})

        await manager.delete(42)

        fake.get.assert_not_called()
        fake.post.assert_not_called()
        fake.put.assert_not_called()
