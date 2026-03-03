"""Tests for the ServerManager."""

import pytest

from postmark.models.servers import DeliveryType, ServerColor, TrackLinks

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

SERVER = {
    "ID": 1,
    "Name": "My Server",
    "ApiTokens": ["abc123"],
    "Color": "Blue",
    "SmtpApiActivated": True,
    "RawEmailEnabled": False,
    "DeliveryType": "Live",
    "ServerLink": "https://account.postmarkapp.com/servers/1/streams",
    "InboundAddress": "abc123@inbound.postmarkapp.com",
    "InboundHookUrl": None,
    "BounceHookUrl": None,
    "OpenHookUrl": None,
    "DeliveryHookUrl": None,
    "PostFirstOpenOnly": False,
    "InboundDomain": None,
    "InboundHash": "abc123",
    "InboundSpamThreshold": 5,
    "TrackOpens": True,
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
    async def test_get_success(self, servers):
        manager, fake = servers
        fake.mock_get_response(SERVER)

        server = await manager.get()

        assert server.id == 1
        assert server.name == "My Server"
        assert server.color == ServerColor.BLUE
        assert server.delivery_type == DeliveryType.LIVE
        assert server.track_links == TrackLinks.NONE
        assert server.smtp_api_activated is True
        assert server.track_opens is True
        assert server.api_tokens == ["abc123"]

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, servers):
        manager, fake = servers
        fake.mock_get_response(SERVER)

        await manager.get()

        fake.get.assert_called_once_with("/server")

    @pytest.mark.asyncio
    async def test_get_optional_fields_are_none(self, servers):
        manager, fake = servers
        fake.mock_get_response(SERVER)

        server = await manager.get()

        assert server.inbound_hook_url is None
        assert server.bounce_hook_url is None
        assert server.open_hook_url is None
        assert server.delivery_hook_url is None
        assert server.click_hook_url is None
        assert server.inbound_domain is None

    @pytest.mark.asyncio
    async def test_get_with_webhook_urls(self, servers):
        manager, fake = servers
        fake.mock_get_response(
            _make_server(
                InboundHookUrl="https://example.com/inbound",
                BounceHookUrl="https://example.com/bounce",
                OpenHookUrl="https://example.com/open",
                DeliveryHookUrl="https://example.com/delivery",
                ClickHookUrl="https://example.com/click",
            )
        )

        server = await manager.get()

        assert server.inbound_hook_url == "https://example.com/inbound"
        assert server.bounce_hook_url == "https://example.com/bounce"
        assert server.open_hook_url == "https://example.com/open"
        assert server.delivery_hook_url == "https://example.com/delivery"
        assert server.click_hook_url == "https://example.com/click"

    @pytest.mark.asyncio
    async def test_get_sandbox_delivery_type(self, servers):
        manager, fake = servers
        fake.mock_get_response(_make_server(DeliveryType="Sandbox"))

        server = await manager.get()

        assert server.delivery_type == DeliveryType.SANDBOX

    @pytest.mark.asyncio
    async def test_get_lowercase_color_from_api(self, servers):
        manager, fake = servers
        fake.mock_get_response(_make_server(Color="yellow"))

        server = await manager.get()

        assert server.color == ServerColor.YELLOW

    @pytest.mark.asyncio
    async def test_get_lowercase_track_links_from_api(self, servers):
        manager, fake = servers
        fake.mock_get_response(_make_server(TrackLinks="htmlandtext"))

        server = await manager.get()

        assert server.track_links == TrackLinks.HTML_AND_TEXT


# ---------------------------------------------------------------------------
# Edit server
# ---------------------------------------------------------------------------


class TestEditServer:
    @pytest.mark.asyncio
    async def test_edit_name(self, servers):
        manager, fake = servers
        fake.mock_put_response(_make_server(Name="New Name"))

        server = await manager.edit(name="New Name")

        assert server.name == "New Name"
        fake.put.assert_called_once_with("/server", json={"Name": "New Name"})

    @pytest.mark.asyncio
    async def test_edit_color(self, servers):
        manager, fake = servers
        fake.mock_put_response(_make_server(Color="Green"))

        server = await manager.edit(color=ServerColor.GREEN)

        assert server.color == ServerColor.GREEN
        body = fake.put.call_args[1]["json"]
        assert body["Color"] == "Green"

    @pytest.mark.asyncio
    async def test_edit_track_links(self, servers):
        manager, fake = servers
        fake.mock_put_response(_make_server(TrackLinks="HtmlAndText"))

        server = await manager.edit(track_links=TrackLinks.HTML_AND_TEXT)

        assert server.track_links == TrackLinks.HTML_AND_TEXT
        body = fake.put.call_args[1]["json"]
        assert body["TrackLinks"] == "HtmlAndText"

    @pytest.mark.asyncio
    async def test_edit_multiple_fields(self, servers):
        manager, fake = servers
        fake.mock_put_response(
            _make_server(
                TrackOpens=False,
                InboundSpamThreshold=10,
                RawEmailEnabled=True,
            )
        )

        await manager.edit(
            track_opens=False,
            inbound_spam_threshold=10,
            raw_email_enabled=True,
        )

        body = fake.put.call_args[1]["json"]
        assert body == {
            "TrackOpens": False,
            "InboundSpamThreshold": 10,
            "RawEmailEnabled": True,
        }

    @pytest.mark.asyncio
    async def test_edit_no_args_sends_empty_body(self, servers):
        manager, fake = servers
        fake.mock_put_response(SERVER)

        await manager.edit()

        fake.put.assert_called_once_with("/server", json={})

    @pytest.mark.asyncio
    async def test_edit_webhook_urls(self, servers):
        manager, fake = servers
        fake.mock_put_response(
            _make_server(
                BounceHookUrl="https://example.com/bounce",
                OpenHookUrl="https://example.com/open",
            )
        )

        await manager.edit(
            bounce_hook_url="https://example.com/bounce",
            open_hook_url="https://example.com/open",
        )

        body = fake.put.call_args[1]["json"]
        assert body["BounceHookUrl"] == "https://example.com/bounce"
        assert body["OpenHookUrl"] == "https://example.com/open"

    @pytest.mark.asyncio
    async def test_edit_calls_put_not_get(self, servers):
        manager, fake = servers
        fake.mock_put_response(SERVER)

        await manager.edit(name="Test")

        fake.put.assert_called_once()
        fake.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_boolean_fields(self, servers):
        manager, fake = servers
        fake.mock_put_response(
            _make_server(
                SmtpApiActivated=False,
                PostFirstOpenOnly=True,
                IncludeBounceContentInHook=True,
                EnableSmtpApiErrorHooks=True,
            )
        )

        await manager.edit(
            smtp_api_activated=False,
            post_first_open_only=True,
            include_bounce_content_in_hook=True,
            enable_smtp_api_error_hooks=True,
        )

        body = fake.put.call_args[1]["json"]
        assert body["SmtpApiActivated"] is False
        assert body["PostFirstOpenOnly"] is True
        assert body["IncludeBounceContentInHook"] is True
        assert body["EnableSmtpApiErrorHooks"] is True
