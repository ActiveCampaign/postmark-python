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


# Shape captured from the live API: per-trigger "Status" on enabled triggers,
# stored Basic auth and a custom header.
LIVE_WEBHOOK = {
    "ID": 1,
    "Url": "https://old.example.com/hook",
    "MessageStream": "outbound",
    "HttpAuth": {"Username": "user", "Password": "pass"},
    "HttpHeaders": [{"Name": "X-Custom", "Value": "sdk"}],
    "Triggers": {
        "Open": {"Enabled": False, "PostFirstOpenOnly": False},
        "Click": {"Enabled": False},
        "Delivery": {"Enabled": True, "Status": "verified"},
        "Bounce": {"Enabled": True, "IncludeContent": True, "Status": "verified"},
        "SpamComplaint": {"Enabled": False, "IncludeContent": False},
        "SubscriptionChange": {"Enabled": False},
    },
}

EXPECTED_TRIGGERS_NO_STATUS = {
    "Open": {"Enabled": False, "PostFirstOpenOnly": False},
    "Click": {"Enabled": False},
    "Delivery": {"Enabled": True},
    "Bounce": {"Enabled": True, "IncludeContent": True},
    "SpamComplaint": {"Enabled": False, "IncludeContent": False},
    "SubscriptionChange": {"Enabled": False},
}


class TestEditWebhook:
    """Postmark's PUT requires Url and verifies using only the request body, so
    edit() reads the current webhook and sends the complete merged configuration."""

    @pytest.fixture
    def live(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(LIVE_WEBHOOK)
        fake.mock_put_response(LIVE_WEBHOOK)
        return manager, fake

    @pytest.mark.asyncio
    async def test_edit_url_keeps_everything_else(self, live):
        manager, fake = live
        fake.mock_put_response({**LIVE_WEBHOOK, "Url": "https://new.com/hook"})

        wh = await manager.edit(1, url="https://new.com/hook")

        assert wh.url == "https://new.com/hook"
        fake.put.assert_called_once_with(
            "/webhooks/1",
            json={
                "Url": "https://new.com/hook",
                "HttpAuth": {"Username": "user", "Password": "pass"},
                "HttpHeaders": [{"Name": "X-Custom", "Value": "sdk"}],
                "Triggers": EXPECTED_TRIGGERS_NO_STATUS,
            },
        )

    @pytest.mark.asyncio
    async def test_edit_without_url_uses_current_url(self, live):
        """The live API rejects a PUT without Url (error 1354)."""
        manager, fake = live

        await manager.edit(1, triggers={"Bounce": {"Enabled": False}})

        assert fake.put.call_args[1]["json"]["Url"] == "https://old.example.com/hook"

    @pytest.mark.asyncio
    async def test_reads_current_webhook_first(self, live):
        manager, fake = live
        order = []
        fake.get.side_effect = lambda *a, **k: (
            order.append("get") or fake.get.return_value
        )
        fake.put.side_effect = lambda *a, **k: (
            order.append("put") or fake.put.return_value
        )

        await manager.edit(7, url="https://x.com/h")

        assert order == ["get", "put"]
        fake.get.assert_called_once_with("/webhooks/7")
        assert fake.put.call_args[0][0] == "/webhooks/7"

    @pytest.mark.asyncio
    async def test_trigger_status_is_not_sent_back(self, live):
        manager, fake = live

        await manager.edit(1, url="https://x.com/h")

        sent = fake.put.call_args[1]["json"]["Triggers"]
        assert all("Status" not in cfg for cfg in sent.values())

    @pytest.mark.asyncio
    async def test_triggers_merge_field_by_field(self, live):
        manager, fake = live

        await manager.edit(1, triggers={"Bounce": {"IncludeContent": False}})

        sent = fake.put.call_args[1]["json"]["Triggers"]
        assert sent["Bounce"] == {"Enabled": True, "IncludeContent": False}
        assert sent["Delivery"] == {"Enabled": True}
        assert sent["Open"] == {"Enabled": False, "PostFirstOpenOnly": False}

    @pytest.mark.asyncio
    async def test_triggers_can_enable_a_new_trigger(self, live):
        manager, fake = live

        await manager.edit(1, triggers={"Click": {"Enabled": True}})

        sent = fake.put.call_args[1]["json"]["Triggers"]
        assert sent["Click"] == {"Enabled": True}
        assert sent["Delivery"] == {"Enabled": True}

    @pytest.mark.asyncio
    async def test_unknown_trigger_name_is_passed_through(self, live):
        manager, fake = live

        await manager.edit(1, triggers={"Brand New": {"Enabled": True}})

        assert fake.put.call_args[1]["json"]["Triggers"]["Brand New"] == {
            "Enabled": True
        }

    @pytest.mark.asyncio
    async def test_edit_with_http_auth_replaces_stored_auth(self, live):
        manager, fake = live

        await manager.edit(1, http_auth={"Username": "u", "Password": "p"})

        body = fake.put.call_args[1]["json"]
        assert body["HttpAuth"] == {"Username": "u", "Password": "p"}
        assert body["HttpHeaders"] == [{"Name": "X-Custom", "Value": "sdk"}]

    @pytest.mark.asyncio
    async def test_edit_http_headers_replace_and_empty_list_clears(self, live):
        manager, fake = live

        await manager.edit(1, http_headers=[{"Name": "X-A", "Value": "1"}])
        assert fake.put.call_args[1]["json"]["HttpHeaders"] == [
            {"Name": "X-A", "Value": "1"}
        ]

        await manager.edit(1, http_headers=[])
        assert fake.put.call_args[1]["json"]["HttpHeaders"] == []

    @pytest.mark.asyncio
    async def test_edit_no_args_resaves_current_configuration(self, live):
        manager, fake = live

        await manager.edit(1)

        assert fake.put.call_args[1]["json"] == {
            "Url": "https://old.example.com/hook",
            "HttpAuth": {"Username": "user", "Password": "pass"},
            "HttpHeaders": [{"Name": "X-Custom", "Value": "sdk"}],
            "Triggers": EXPECTED_TRIGGERS_NO_STATUS,
        }

    @pytest.mark.asyncio
    async def test_webhook_without_auth_or_headers_sends_neither(self, webhooks):
        """Live responses omit HttpAuth/HttpHeaders entirely when unset."""
        manager, fake = webhooks
        bare = {
            "ID": 2,
            "Url": "https://bare.example.com",
            "MessageStream": "outbound",
            "Triggers": {
                **EXPECTED_TRIGGERS_NO_STATUS,
                "Delivery": {"Enabled": True, "Status": "verified"},
            },
        }
        fake.mock_get_response(bare)
        fake.mock_put_response(bare)

        await manager.edit(2, url="https://bare2.example.com")

        assert fake.put.call_args[1]["json"] == {
            "Url": "https://bare2.example.com",
            "Triggers": EXPECTED_TRIGGERS_NO_STATUS,
        }

    @pytest.mark.asyncio
    async def test_webhook_without_triggers_sends_none(self, webhooks):
        manager, fake = webhooks
        bare = {"ID": 3, "Url": "https://t.example.com", "MessageStream": "outbound"}
        fake.mock_get_response(bare)
        fake.mock_put_response(WEBHOOK)

        await manager.edit(3, url="https://t2.example.com")

        assert fake.put.call_args[1]["json"] == {"Url": "https://t2.example.com"}

    @pytest.mark.asyncio
    async def test_failed_read_prevents_the_write(self, webhooks):
        manager, fake = webhooks
        fake.get.side_effect = RuntimeError("not found")

        with pytest.raises(RuntimeError):
            await manager.edit(99, url="https://x.com/h")

        fake.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_returns_updated_webhook(self, live):
        manager, fake = live
        fake.mock_put_response({**LIVE_WEBHOOK, "Url": "https://new.com/hook"})

        wh = await manager.edit(1, url="https://new.com/hook")

        assert wh.id == 1
        assert wh.url == "https://new.com/hook"


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
