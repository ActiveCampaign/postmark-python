"""Tests for InboundRuleManager."""

import pytest

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

RULE = {"ID": 1, "Rule": "spam@example.com"}
DELETE_RESPONSE = {"ErrorCode": 0, "Message": "Trigger removed."}


def _make_list(rules: list) -> dict:
    return {"TotalCount": len(rules), "InboundRules": rules}


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


class TestListInboundRules:
    @pytest.mark.asyncio
    async def test_list_success(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_get_response(_make_list([RULE, {"ID": 2, "Rule": "example.com"}]))

        result = await manager.list()

        assert result.total == 2
        assert result.items[0].id == 1
        assert result.items[0].rule == "spam@example.com"
        assert result.items[1].rule == "example.com"

    @pytest.mark.asyncio
    async def test_list_default_params(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_get_response(_make_list([]))

        await manager.list()

        fake.get.assert_called_once_with(
            "/triggers/inboundrules", params={"count": 100, "offset": 0}
        )

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_get_response(_make_list([]))

        await manager.list(count=10, offset=20)

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 10
        assert params["offset"] == 20

    @pytest.mark.asyncio
    async def test_list_empty(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_get_response(_make_list([]))

        result = await manager.list()

        assert result.total == 0
        assert result.items == []


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


class TestCreateInboundRule:
    @pytest.mark.asyncio
    async def test_create_success(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_post_response(RULE)

        rule = await manager.create("spam@example.com")

        assert rule.id == 1
        assert rule.rule == "spam@example.com"

    @pytest.mark.asyncio
    async def test_create_calls_correct_endpoint(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_post_response(RULE)

        await manager.create("spam@example.com")

        fake.post.assert_called_once_with(
            "/triggers/inboundrules", json={"Rule": "spam@example.com"}
        )

    @pytest.mark.asyncio
    async def test_create_domain_rule(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_post_response({"ID": 2, "Rule": "example.com"})

        rule = await manager.create("example.com")

        assert rule.rule == "example.com"
        body = fake.post.call_args[1]["json"]
        assert body["Rule"] == "example.com"


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


class TestDeleteInboundRule:
    @pytest.mark.asyncio
    async def test_delete_success(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_delete_response(DELETE_RESPONSE)

        result = await manager.delete(1)

        assert result.error_code == 0
        assert result.message == "Trigger removed."

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(1)

        fake.delete.assert_called_once_with("/triggers/inboundrules/1")

    @pytest.mark.asyncio
    async def test_delete_does_not_call_other_methods(self, inbound_rules):
        manager, fake = inbound_rules
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(1)

        fake.get.assert_not_called()
        fake.post.assert_not_called()
        fake.put.assert_not_called()
