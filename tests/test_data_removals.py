"""Tests for DataRemovalManager."""

import pytest

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

REMOVAL = {"ID": 42, "Status": "Pending"}
REMOVAL_DONE = {"ID": 42, "Status": "Done"}


# ---------------------------------------------------------------------------
# Create data removal
# ---------------------------------------------------------------------------


class TestCreateDataRemoval:
    @pytest.mark.asyncio
    async def test_create_success(self, data_removals):
        manager, fake = data_removals
        fake.mock_post_response(REMOVAL)

        result = await manager.create(
            requested_by="admin@example.com",
            requested_for="user@example.com",
        )

        assert result.id == 42
        assert result.status == "Pending"

    @pytest.mark.asyncio
    async def test_create_calls_correct_endpoint(self, data_removals):
        manager, fake = data_removals
        fake.mock_post_response(REMOVAL)

        await manager.create(
            requested_by="admin@example.com",
            requested_for="user@example.com",
        )

        fake.post.assert_called_once_with(
            "/data-removals",
            json={
                "RequestedBy": "admin@example.com",
                "RequestedFor": "user@example.com",
                "NotifyWhenCompleted": False,
            },
        )

    @pytest.mark.asyncio
    async def test_create_with_notify(self, data_removals):
        manager, fake = data_removals
        fake.mock_post_response(REMOVAL)

        await manager.create(
            requested_by="admin@example.com",
            requested_for="user@example.com",
            notify_when_completed=True,
        )

        body = fake.post.call_args[1]["json"]
        assert body["NotifyWhenCompleted"] is True


# ---------------------------------------------------------------------------
# Get data removal
# ---------------------------------------------------------------------------


class TestGetDataRemoval:
    @pytest.mark.asyncio
    async def test_get_success(self, data_removals):
        manager, fake = data_removals
        fake.mock_get_response(REMOVAL_DONE)

        result = await manager.get(42)

        assert result.id == 42
        assert result.status == "Done"

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, data_removals):
        manager, fake = data_removals
        fake.mock_get_response(REMOVAL)

        await manager.get(42)

        fake.get.assert_called_once_with("/data-removals/42")
