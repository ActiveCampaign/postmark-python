"""Tests for WebhookManager."""

import pytest

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

TRIGGERS = {
    "Open": {"Enabled": True, "PostFirstOpenOnly": False},
    "Click": {"Enabled": False},
    "Delivery": {"Enabled": False},
    "Bounce": {"Enabled": True, "IncludeContent": False},
    "SpamComplaint": {"Enabled": False, "IncludeContent": False},
    "SubscriptionChange": {"Enabled": False},
}

WEBHOOK = {
    "ID": 1,
    "Url": "https://example.com/webhook",
    "MessageStream": "outbound",
    "HttpAuth": None,
    "HttpHeaders": [],
    "Triggers": TRIGGERS,
}

DELETE_RESPONSE = {"ErrorCode": 0, "Message": "Webhook removed."}


def _make_webhook(**overrides) -> dict:
    return {**WEBHOOK, **overrides}


# ---------------------------------------------------------------------------
# List webhooks
# ---------------------------------------------------------------------------


class TestListWebhooks:
    @pytest.mark.asyncio
    async def test_list_success(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(
            {"Webhooks": [WEBHOOK, _make_webhook(ID=2, Url="https://other.com/hook")]}
        )

        result = await manager.list()

        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].url == "https://example.com/webhook"
        assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_list_no_filter(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response({"Webhooks": []})

        await manager.list()

        fake.get.assert_called_once_with("/webhooks", params={})

    @pytest.mark.asyncio
    async def test_list_with_message_stream(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response({"Webhooks": []})

        await manager.list(message_stream="outbound")

        params = fake.get.call_args[1]["params"]
        assert params["MessageStream"] == "outbound"

    @pytest.mark.asyncio
    async def test_list_empty(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response({"Webhooks": []})

        result = await manager.list()

        assert result == []

    @pytest.mark.asyncio
    async def test_list_parses_triggers(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response({"Webhooks": [WEBHOOK]})

        result = await manager.list()

        assert result[0].triggers.open.enabled is True
        assert result[0].triggers.bounce.include_content is False


# ---------------------------------------------------------------------------
# Get webhook
# ---------------------------------------------------------------------------


class TestGetWebhook:
    @pytest.mark.asyncio
    async def test_get_success(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(WEBHOOK)

        wh = await manager.get(1)

        assert wh.id == 1
        assert wh.url == "https://example.com/webhook"
        assert wh.message_stream == "outbound"

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(WEBHOOK)

        await manager.get(1)

        fake.get.assert_called_once_with("/webhooks/1")


# ---------------------------------------------------------------------------
# Create webhook
# ---------------------------------------------------------------------------


class TestCreateWebhook:
    @pytest.mark.asyncio
    async def test_create_url_only(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        wh = await manager.create(url="https://example.com/webhook")

        assert wh.id == 1
        fake.post.assert_called_once_with(
            "/webhooks", json={"Url": "https://example.com/webhook"}
        )

    @pytest.mark.asyncio
    async def test_create_with_message_stream(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create(
            url="https://example.com/webhook", message_stream="outbound"
        )

        body = fake.post.call_args[1]["json"]
        assert body["MessageStream"] == "outbound"

    @pytest.mark.asyncio
    async def test_create_with_http_auth(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create(
            url="https://example.com/webhook",
            http_auth={"Username": "user", "Password": "pass"},
        )

        body = fake.post.call_args[1]["json"]
        assert body["HttpAuth"] == {"Username": "user", "Password": "pass"}

    @pytest.mark.asyncio
    async def test_create_with_http_headers(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create(
            url="https://example.com/webhook",
            http_headers=[{"Name": "X-Custom", "Value": "val"}],
        )

        body = fake.post.call_args[1]["json"]
        assert body["HttpHeaders"] == [{"Name": "X-Custom", "Value": "val"}]

    @pytest.mark.asyncio
    async def test_create_with_triggers(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        triggers = {"Open": {"Enabled": True, "PostFirstOpenOnly": False}}
        await manager.create(url="https://example.com/webhook", triggers=triggers)

        body = fake.post.call_args[1]["json"]
        assert body["Triggers"] == triggers

    @pytest.mark.asyncio
    async def test_create_omits_none_fields(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create(url="https://example.com/webhook")

        body = fake.post.call_args[1]["json"]
        assert "MessageStream" not in body
        assert "HttpAuth" not in body
        assert "HttpHeaders" not in body
        assert "Triggers" not in body


# ---------------------------------------------------------------------------
# Edit webhook
# ---------------------------------------------------------------------------


class TestEditWebhook:
    @pytest.mark.asyncio
    async def test_edit_url(self, webhooks):
        manager, fake = webhooks
        fake.mock_put_response(_make_webhook(Url="https://new.com/hook"))

        wh = await manager.edit(1, url="https://new.com/hook")

        assert wh.url == "https://new.com/hook"
        fake.put.assert_called_once_with(
            "/webhooks/1", json={"Url": "https://new.com/hook"}
        )

    @pytest.mark.asyncio
    async def test_edit_no_args_sends_empty_body(self, webhooks):
        manager, fake = webhooks
        fake.mock_put_response(WEBHOOK)

        await manager.edit(1)

        fake.put.assert_called_once_with("/webhooks/1", json={})

    @pytest.mark.asyncio
    async def test_edit_calls_correct_endpoint(self, webhooks):
        manager, fake = webhooks
        fake.mock_put_response(WEBHOOK)

        await manager.edit(99, url="https://example.com/hook")

        fake.put.assert_called_once_with(
            "/webhooks/99", json={"Url": "https://example.com/hook"}
        )

    @pytest.mark.asyncio
    async def test_edit_with_triggers(self, webhooks):
        manager, fake = webhooks
        fake.mock_put_response(WEBHOOK)

        triggers = {"Bounce": {"Enabled": True, "IncludeContent": True}}
        await manager.edit(1, triggers=triggers)

        body = fake.put.call_args[1]["json"]
        assert body["Triggers"] == triggers

    @pytest.mark.asyncio
    async def test_edit_with_http_auth(self, webhooks):
        manager, fake = webhooks
        fake.mock_put_response(WEBHOOK)

        await manager.edit(1, http_auth={"Username": "u", "Password": "p"})

        body = fake.put.call_args[1]["json"]
        assert body["HttpAuth"] == {"Username": "u", "Password": "p"}


# ---------------------------------------------------------------------------
# Delete webhook
# ---------------------------------------------------------------------------


class TestDeleteWebhook:
    @pytest.mark.asyncio
    async def test_delete_success(self, webhooks):
        manager, fake = webhooks
        fake.mock_delete_response(DELETE_RESPONSE)

        result = await manager.delete(1)

        assert result.error_code == 0
        assert result.message == "Webhook removed."

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self, webhooks):
        manager, fake = webhooks
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(1)

        fake.delete.assert_called_once_with("/webhooks/1")

    @pytest.mark.asyncio
    async def test_delete_does_not_call_other_methods(self, webhooks):
        manager, fake = webhooks
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(1)

        fake.get.assert_not_called()
        fake.post.assert_not_called()
        fake.put.assert_not_called()
