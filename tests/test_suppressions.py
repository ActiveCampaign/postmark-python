"""Tests for SuppressionManager."""

from datetime import date

import pytest

from postmark.models.suppressions import SuppressionOrigin, SuppressionReason

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

SUPPRESSION_ENTRY = {
    "EmailAddress": "user@example.com",
    "SuppressionReason": "HardBounce",
    "Origin": "Recipient",
    "CreatedAt": "2024-01-15T00:00:00Z",
}

CREATE_RESULT = {
    "EmailAddress": "user@example.com",
    "Status": "Suppressed",
    "Message": None,
}

DELETE_RESULT = {
    "EmailAddress": "user@example.com",
    "Status": "Deleted",
    "Message": None,
}

FAILED_RESULT = {
    "EmailAddress": "bad@example.com",
    "Status": "Failed",
    "Message": "Address not found.",
}


# ---------------------------------------------------------------------------
# Dump
# ---------------------------------------------------------------------------


class TestDumpSuppressions:
    @pytest.mark.asyncio
    async def test_dump_success(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": [SUPPRESSION_ENTRY]})

        result = await manager.dump("outbound")

        assert len(result) == 1
        assert result[0].email_address == "user@example.com"
        assert result[0].suppression_reason == SuppressionReason.HARD_BOUNCE
        assert result[0].origin == SuppressionOrigin.RECIPIENT

    @pytest.mark.asyncio
    async def test_dump_calls_correct_endpoint(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": []})

        await manager.dump("outbound")

        fake.get.assert_called_once_with(
            "/message-streams/outbound/suppressions/dump", params={}
        )

    @pytest.mark.asyncio
    async def test_dump_with_suppression_reason(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": []})

        await manager.dump("outbound", suppression_reason=SuppressionReason.HARD_BOUNCE)

        params = fake.get.call_args[1]["params"]
        assert params["SuppressionReason"] == "HardBounce"

    @pytest.mark.asyncio
    async def test_dump_with_origin(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": []})

        await manager.dump("outbound", origin=SuppressionOrigin.RECIPIENT)

        params = fake.get.call_args[1]["params"]
        assert params["Origin"] == "Recipient"

    @pytest.mark.asyncio
    async def test_dump_with_date_range(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": []})

        await manager.dump(
            "outbound",
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
        )

        params = fake.get.call_args[1]["params"]
        assert params["fromdate"] == "2024-01-01"
        assert params["todate"] == "2024-01-31"

    @pytest.mark.asyncio
    async def test_dump_with_email_address(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": []})

        await manager.dump("outbound", email_address="user@example.com")

        params = fake.get.call_args[1]["params"]
        assert params["EmailAddress"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_dump_different_stream(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": []})

        await manager.dump("broadcasts")

        fake.get.assert_called_once_with(
            "/message-streams/broadcasts/suppressions/dump", params={}
        )

    @pytest.mark.asyncio
    async def test_dump_empty(self, suppressions):
        manager, fake = suppressions
        fake.mock_get_response({"Suppressions": []})

        result = await manager.dump("outbound")

        assert result == []


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


class TestCreateSuppression:
    @pytest.mark.asyncio
    async def test_create_single(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": [CREATE_RESULT]})

        result = await manager.create("outbound", ["user@example.com"])

        assert len(result) == 1
        assert result[0].email_address == "user@example.com"
        assert result[0].status == "Suppressed"

    @pytest.mark.asyncio
    async def test_create_multiple(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response(
            {
                "Suppressions": [
                    CREATE_RESULT,
                    {**CREATE_RESULT, "EmailAddress": "other@example.com"},
                ]
            }
        )

        result = await manager.create(
            "outbound", ["user@example.com", "other@example.com"]
        )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_create_calls_correct_endpoint(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": [CREATE_RESULT]})

        await manager.create("outbound", ["user@example.com"])

        fake.post.assert_called_once_with(
            "/message-streams/outbound/suppressions",
            json={"Suppressions": [{"EmailAddress": "user@example.com"}]},
        )

    @pytest.mark.asyncio
    async def test_create_formats_body_correctly(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": []})

        await manager.create("outbound", ["a@example.com", "b@example.com"])

        body = fake.post.call_args[1]["json"]
        assert body == {
            "Suppressions": [
                {"EmailAddress": "a@example.com"},
                {"EmailAddress": "b@example.com"},
            ]
        }

    @pytest.mark.asyncio
    async def test_create_failed_result(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": [FAILED_RESULT]})

        result = await manager.create("outbound", ["bad@example.com"])

        assert result[0].status == "Failed"
        assert result[0].message == "Address not found."


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


class TestDeleteSuppression:
    @pytest.mark.asyncio
    async def test_delete_single(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": [DELETE_RESULT]})

        result = await manager.delete("outbound", ["user@example.com"])

        assert len(result) == 1
        assert result[0].email_address == "user@example.com"
        assert result[0].status == "Deleted"

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": [DELETE_RESULT]})

        await manager.delete("outbound", ["user@example.com"])

        fake.post.assert_called_once_with(
            "/message-streams/outbound/suppressions/delete",
            json={"Suppressions": [{"EmailAddress": "user@example.com"}]},
        )

    @pytest.mark.asyncio
    async def test_delete_formats_body_correctly(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": []})

        await manager.delete("outbound", ["a@example.com", "b@example.com"])

        body = fake.post.call_args[1]["json"]
        assert body == {
            "Suppressions": [
                {"EmailAddress": "a@example.com"},
                {"EmailAddress": "b@example.com"},
            ]
        }

    @pytest.mark.asyncio
    async def test_delete_different_stream(self, suppressions):
        manager, fake = suppressions
        fake.mock_post_response({"Suppressions": []})

        await manager.delete("broadcasts", ["user@example.com"])

        args, kwargs = fake.post.call_args
        assert args[0] == "/message-streams/broadcasts/suppressions/delete"
