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


# ---------------------------------------------------------------------------
# Webhook statistics (shape captured from the live API)
# ---------------------------------------------------------------------------

_ZERO_METRICS = {
    "TotalRequests": 0,
    "SuccessCount": 0,
    "FailureCount": 0,
    "RetryCount": 0,
    "SuccessRate": 0,
    "SlowCount": 0,
    "VerySlowCount": 0,
}

STATISTICS = {
    "WebhookId": 1234,
    "ServerId": 11111,
    "MessageStreamId": "outbound",
    "Url": "https://example.com/hook",
    "Statuses": {"Open": "verified", "Delivery": "verified"},
    "TimeRange": {
        "StartTime": "2026-10-20T20:00:00Z",
        "EndTime": "2026-10-21T20:28:07.9440221Z",
        "Hours": 24,
    },
    "Metrics": {
        "TotalRequests": 1,
        "SuccessCount": 1,
        "FailureCount": 0,
        "RetryCount": 0,
        "SuccessRate": 100,
        "SlowCount": 0,
        "VerySlowCount": 0,
        "AverageTerminalResponseTimeMs": 98,
    },
    "MetricsByTrigger": {
        "Open": _ZERO_METRICS,
        "Delivery": {
            "TotalRequests": 1,
            "SuccessCount": 1,
            "FailureCount": 0,
            "RetryCount": 0,
            "SuccessRate": 100,
            "SlowCount": 0,
            "VerySlowCount": 0,
            "AverageTerminalResponseTimeMs": 98,
        },
    },
}


class TestWebhookStatistics:
    @pytest.mark.asyncio
    async def test_calls_the_statistics_endpoint(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(STATISTICS)

        await manager.get_statistics(1234)

        fake.get.assert_called_once_with("/webhooks/1234/statistics")

    @pytest.mark.asyncio
    async def test_parses_identity_window_and_statuses(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(STATISTICS)

        stats = await manager.get_statistics(1234)

        assert stats.webhook_id == 1234
        assert stats.server_id == 11111
        assert stats.message_stream_id == "outbound"
        assert stats.url == "https://example.com/hook"
        assert stats.statuses == {"Open": "verified", "Delivery": "verified"}
        assert stats.time_range.hours == 24
        assert stats.time_range.start_time.isoformat() == "2026-10-20T20:00:00+00:00"
        assert stats.time_range.end_time.year == 2026

    @pytest.mark.asyncio
    async def test_parses_overall_metrics(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(STATISTICS)

        m = (await manager.get_statistics(1)).metrics

        assert (m.total_requests, m.success_count, m.failure_count) == (1, 1, 0)
        assert m.retry_count == 0
        assert m.success_rate == 100.0
        assert (m.slow_count, m.very_slow_count) == (0, 0)
        assert m.average_terminal_response_time_ms == 98

    @pytest.mark.asyncio
    async def test_parses_metrics_by_trigger(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(STATISTICS)

        by_trigger = (await manager.get_statistics(1)).metrics_by_trigger

        assert set(by_trigger) == {"Open", "Delivery"}
        assert by_trigger["Delivery"].total_requests == 1
        assert by_trigger["Open"].total_requests == 0

    @pytest.mark.asyncio
    async def test_averages_are_none_without_traffic_or_retries(self, webhooks):
        """The averages are absent from the response when nothing was sent."""
        manager, fake = webhooks
        fake.mock_get_response({**STATISTICS, "Metrics": _ZERO_METRICS})

        m = (await manager.get_statistics(1)).metrics

        assert m.average_terminal_response_time_ms is None
        assert m.average_retry_response_time_ms is None

    @pytest.mark.asyncio
    async def test_retry_average_when_present(self, webhooks):
        manager, fake = webhooks
        metrics = {
            **_ZERO_METRICS,
            "RetryCount": 2,
            "AverageRetryResponseTimeMs": 310.5,
        }
        fake.mock_get_response({**STATISTICS, "Metrics": metrics})

        m = (await manager.get_statistics(1)).metrics

        assert m.retry_count == 2
        assert m.average_retry_response_time_ms == 310.5

    @pytest.mark.asyncio
    async def test_minimal_response_uses_defaults(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response({"WebhookId": 5})

        stats = await manager.get_statistics(5)

        assert stats.webhook_id == 5
        assert stats.statuses == {}
        assert stats.time_range is None
        assert stats.metrics_by_trigger == {}
        assert stats.metrics.total_requests == 0
        assert stats.url is None

    @pytest.mark.asyncio
    async def test_unknown_trigger_and_status_values_do_not_break_parsing(
        self, webhooks
    ):
        manager, fake = webhooks
        fake.mock_get_response(
            {
                **STATISTICS,
                "Statuses": {"BrandNew": "pending"},
                "MetricsByTrigger": {"BrandNew": _ZERO_METRICS},
            }
        )

        stats = await manager.get_statistics(1)

        assert stats.statuses == {"BrandNew": "pending"}
        assert "BrandNew" in stats.metrics_by_trigger


# ---------------------------------------------------------------------------
# Webhook verification (responses captured from the live API)
# ---------------------------------------------------------------------------

VERIFY_OK = {
    "Id": 101,
    "Url": "https://example.com/hook",
    "Success": True,
    "Results": [
        {
            "TriggerType": "Open",
            "Success": True,
            "StatusCode": 200,
            "Message": "Success!",
        },
        {
            "TriggerType": "Delivery",
            "Success": True,
            "StatusCode": 200,
            "Message": "Success!",
        },
    ],
    "Message": "All 2 triggers verified successfully",
}

VERIFY_REJECTED = {
    "Id": 102,
    "Url": "https://example.com/hook",
    "Success": False,
    "Results": [
        {
            "TriggerType": "Delivery",
            "Success": False,
            "StatusCode": 401,
            "Message": "ok",
        },
        {
            "TriggerType": "Bounce",
            "Success": False,
            "StatusCode": 401,
            "Message": "ok",
        },
    ],
    "Message": "0/2 triggers verified successfully",
}

VERIFY_UNREACHABLE = {
    "Id": 103,
    "Url": "https://no-such-host.invalid/hook",
    "Success": False,
    "Results": [
        {
            "TriggerType": "Delivery",
            "Success": False,
            "StatusCode": 0,
            "Message": "The request failed due to a SocketException, which means "
            "the webhook url could not be reached.",
        }
    ],
    "Message": "0/1 triggers verified successfully",
}

VERIFY_NO_TRIGGERS = {
    "Id": 104,
    "Url": "https://example.com/hook",
    "Success": False,
    "Results": [],
    "Message": "No triggers configured for this webhook",
}


class TestVerifyWebhook:
    @pytest.mark.asyncio
    async def test_posts_to_the_verify_endpoint_without_a_body(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(VERIFY_OK)

        await manager.verify(101)

        fake.post.assert_called_once_with("/webhooks/101/verify")

    @pytest.mark.asyncio
    async def test_successful_verification(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(VERIFY_OK)

        result = await manager.verify(101)

        assert result.success is True
        assert result.id == 101
        assert result.url == "https://example.com/hook"
        assert result.message == "All 2 triggers verified successfully"
        assert [(r.trigger_type, r.success, r.status_code) for r in result.results] == [
            ("Open", True, 200),
            ("Delivery", True, 200),
        ]
        assert result.results[0].message == "Success!"

    @pytest.mark.asyncio
    async def test_rejecting_endpoint_is_returned_not_raised(self, webhooks):
        """Postmark answers HTTP 200 with Success=false; the caller inspects it."""
        manager, fake = webhooks
        fake.mock_post_response(VERIFY_REJECTED)

        result = await manager.verify(102)

        assert result.success is False
        assert all(r.status_code == 401 for r in result.results)
        assert result.message == "0/2 triggers verified successfully"

    @pytest.mark.asyncio
    async def test_unreachable_endpoint_reports_status_code_zero(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(VERIFY_UNREACHABLE)

        result = await manager.verify(103)

        assert result.success is False
        assert result.results[0].status_code == 0
        assert "could not be reached" in result.results[0].message

    @pytest.mark.asyncio
    async def test_no_triggers_enabled(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(VERIFY_NO_TRIGGERS)

        result = await manager.verify(104)

        assert result.success is False
        assert result.results == []
        assert result.message == "No triggers configured for this webhook"

    @pytest.mark.asyncio
    async def test_minimal_response(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response({"Id": 7, "Success": True})

        result = await manager.verify(7)

        assert result.success is True
        assert result.results == []
        assert result.url is None
        assert result.message is None

    @pytest.mark.asyncio
    async def test_unknown_trigger_type_does_not_break_parsing(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(
            {
                "Id": 7,
                "Success": True,
                "Results": [{"TriggerType": "BrandNew", "Success": True}],
            }
        )

        result = await manager.verify(7)

        assert result.results[0].trigger_type == "BrandNew"
        assert result.results[0].status_code is None


# ---------------------------------------------------------------------------
# verify=False: Postmark takes it as the ?verify=false QUERY parameter. A body
# field named "Verify" is silently ignored by the API (verified live).
# ---------------------------------------------------------------------------


class TestSkipVerification:
    @pytest.mark.asyncio
    async def test_create_verifies_by_default(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create("https://example.com/hook")

        assert fake.post.call_args[0][0] == "/webhooks"

    @pytest.mark.asyncio
    async def test_create_explicit_true_is_the_same_as_the_default(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create("https://example.com/hook", verify=True)

        assert fake.post.call_args[0][0] == "/webhooks"

    @pytest.mark.asyncio
    async def test_create_without_verification_uses_the_query_parameter(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create("https://example.com/hook", verify=False)

        assert fake.post.call_args[0][0] == "/webhooks?verify=false"

    @pytest.mark.asyncio
    async def test_create_never_puts_verify_in_the_body(self, webhooks):
        manager, fake = webhooks
        fake.mock_post_response(WEBHOOK)

        await manager.create("https://example.com/hook", verify=False)

        body = fake.post.call_args[1]["json"]
        assert "Verify" not in body
        assert "verify" not in body
        assert body == {"Url": "https://example.com/hook"}

    @pytest.mark.asyncio
    async def test_edit_verifies_by_default(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(LIVE_WEBHOOK)
        fake.mock_put_response(LIVE_WEBHOOK)

        await manager.edit(1, url="https://x.com/h")

        assert fake.put.call_args[0][0] == "/webhooks/1"

    @pytest.mark.asyncio
    async def test_edit_without_verification_uses_the_query_parameter(self, webhooks):
        manager, fake = webhooks
        fake.mock_get_response(LIVE_WEBHOOK)
        fake.mock_put_response(LIVE_WEBHOOK)

        await manager.edit(1, url="https://x.com/h", verify=False)

        assert fake.put.call_args[0][0] == "/webhooks/1?verify=false"
        assert "Verify" not in fake.put.call_args[1]["json"]

    @pytest.mark.asyncio
    async def test_edit_reads_the_webhook_without_the_query_parameter(self, webhooks):
        """Only the write is affected; the read-before-write stays a plain GET."""
        manager, fake = webhooks
        fake.mock_get_response(LIVE_WEBHOOK)
        fake.mock_put_response(LIVE_WEBHOOK)

        await manager.edit(5, url="https://x.com/h", verify=False)

        fake.get.assert_called_once_with("/webhooks/5")

    @pytest.mark.asyncio
    async def test_unverified_trigger_status_is_parsed(self, webhooks):
        manager, fake = webhooks
        unverified = {
            **WEBHOOK,
            "Triggers": {
                **TRIGGERS,
                "Delivery": {"Enabled": True, "Status": "unverified"},
            },
        }
        fake.mock_post_response(unverified)

        wh = await manager.create("https://example.com/hook", verify=False)

        assert wh.triggers.delivery.enabled is True
