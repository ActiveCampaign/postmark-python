"""Tests for the StreamManager."""

import pytest

from postmark.models.streams import MessageStreamType, UnsubscribeHandlingType

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

STREAM = {
    "ID": "outbound",
    "ServerID": 23,
    "Name": "Default Transactional Stream",
    "Description": None,
    "MessageStreamType": "Transactional",
    "CreatedAt": "2020-07-09T04:44:46-04:00",
    "UpdatedAt": None,
    "ArchivedAt": None,
    "ExpectedPurgeDate": None,
    "SubscriptionManagementConfiguration": {
        "UnsubscribeHandlingType": "None",
    },
}


def _make_stream(**overrides) -> dict:
    return {**STREAM, **overrides}


# ---------------------------------------------------------------------------
# List message streams
# ---------------------------------------------------------------------------


class TestListStreams:
    @pytest.fixture
    def list_response(self):
        return {
            "TotalCount": 2,
            "MessageStreams": [
                _make_stream(ID="outbound", Name="Transactional"),
                _make_stream(
                    ID="broadcasts", Name="Broadcasts", MessageStreamType="Broadcasts"
                ),
            ],
        }

    @pytest.mark.asyncio
    async def test_list_success(self, streams, list_response):
        manager, fake = streams
        fake.mock_get_response(list_response)

        result, total = await manager.list()

        assert total == 2
        assert len(result) == 2
        assert result[0].id == "outbound"
        assert result[1].id == "broadcasts"

    @pytest.mark.asyncio
    async def test_list_default_params(self, streams):
        manager, fake = streams
        fake.mock_get_response({"TotalCount": 0, "MessageStreams": []})

        await manager.list()

        fake.get.assert_called_once_with(
            "/message-streams", params={"IncludeArchivedStreams": False}
        )

    @pytest.mark.asyncio
    async def test_list_with_type_filter(self, streams):
        manager, fake = streams
        fake.mock_get_response({"TotalCount": 0, "MessageStreams": []})

        await manager.list(message_stream_type=MessageStreamType.TRANSACTIONAL)

        params = fake.get.call_args[1]["params"]
        assert params["MessageStreamType"] == "Transactional"

    @pytest.mark.asyncio
    async def test_list_include_archived(self, streams):
        manager, fake = streams
        fake.mock_get_response({"TotalCount": 0, "MessageStreams": []})

        await manager.list(include_archived=True)

        params = fake.get.call_args[1]["params"]
        assert params["IncludeArchivedStreams"] is True

    @pytest.mark.asyncio
    async def test_list_empty(self, streams):
        manager, fake = streams
        fake.mock_get_response({"TotalCount": 0, "MessageStreams": []})

        result, total = await manager.list()

        assert total == 0
        assert result == []

    @pytest.mark.asyncio
    async def test_list_stream_fields(self, streams):
        manager, fake = streams
        fake.mock_get_response({"TotalCount": 1, "MessageStreams": [STREAM]})

        result, _ = await manager.list()

        stream = result[0]
        assert stream.id == "outbound"
        assert stream.server_id == 23
        assert stream.name == "Default Transactional Stream"
        assert stream.message_stream_type == MessageStreamType.TRANSACTIONAL
        assert stream.description is None
        assert stream.archived_at is None
        assert (
            stream.subscription_management_configuration.unsubscribe_handling_type
            == UnsubscribeHandlingType.NONE
        )


# ---------------------------------------------------------------------------
# Get message stream
# ---------------------------------------------------------------------------


class TestGetStream:
    @pytest.mark.asyncio
    async def test_get_success(self, streams):
        manager, fake = streams
        fake.mock_get_response(STREAM)

        stream = await manager.get("outbound")

        assert stream.id == "outbound"
        assert stream.name == "Default Transactional Stream"
        assert stream.message_stream_type == MessageStreamType.TRANSACTIONAL

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, streams):
        manager, fake = streams
        fake.mock_get_response(STREAM)

        await manager.get("outbound")

        fake.get.assert_called_once_with("/message-streams/outbound")

    @pytest.mark.asyncio
    async def test_get_different_stream_id(self, streams):
        manager, fake = streams
        fake.mock_get_response(_make_stream(ID="broadcasts"))

        await manager.get("broadcasts")

        fake.get.assert_called_once_with("/message-streams/broadcasts")

    @pytest.mark.asyncio
    async def test_get_optional_fields_none(self, streams):
        manager, fake = streams
        fake.mock_get_response(STREAM)

        stream = await manager.get("outbound")

        assert stream.description is None
        assert stream.updated_at is None
        assert stream.archived_at is None
        assert stream.expected_purge_date is None

    @pytest.mark.asyncio
    async def test_get_with_description(self, streams):
        manager, fake = streams
        fake.mock_get_response(_make_stream(Description="My stream description"))

        stream = await manager.get("outbound")

        assert stream.description == "My stream description"

    @pytest.mark.asyncio
    async def test_get_broadcasts_type(self, streams):
        manager, fake = streams
        fake.mock_get_response(
            _make_stream(ID="broadcasts", MessageStreamType="Broadcasts")
        )

        stream = await manager.get("broadcasts")

        assert stream.message_stream_type == MessageStreamType.BROADCASTS

    @pytest.mark.asyncio
    async def test_get_inbound_type(self, streams):
        manager, fake = streams
        fake.mock_get_response(_make_stream(ID="inbound", MessageStreamType="Inbound"))

        stream = await manager.get("inbound")

        assert stream.message_stream_type == MessageStreamType.INBOUND

    @pytest.mark.asyncio
    async def test_get_postmark_unsubscribe_handling(self, streams):
        manager, fake = streams
        fake.mock_get_response(
            _make_stream(
                SubscriptionManagementConfiguration={
                    "UnsubscribeHandlingType": "Postmark"
                }
            )
        )

        stream = await manager.get("outbound")

        assert (
            stream.subscription_management_configuration.unsubscribe_handling_type
            == UnsubscribeHandlingType.POSTMARK
        )


# ---------------------------------------------------------------------------
# Create message stream
# ---------------------------------------------------------------------------


class TestCreateStream:
    @pytest.mark.asyncio
    async def test_create_required_fields(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        stream = await manager.create(
            id="my-stream",
            name="My Stream",
            message_stream_type=MessageStreamType.TRANSACTIONAL,
        )

        assert stream.id == "outbound"
        fake.post.assert_called_once_with(
            "/message-streams",
            json={
                "ID": "my-stream",
                "Name": "My Stream",
                "MessageStreamType": "Transactional",
            },
        )

    @pytest.mark.asyncio
    async def test_create_with_description(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        await manager.create(
            id="my-stream",
            name="My Stream",
            message_stream_type=MessageStreamType.BROADCASTS,
            description="A broadcast stream",
        )

        body = fake.post.call_args[1]["json"]
        assert body["Description"] == "A broadcast stream"
        assert body["MessageStreamType"] == "Broadcasts"

    @pytest.mark.asyncio
    async def test_create_with_unsubscribe_handling(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        await manager.create(
            id="my-stream",
            name="My Stream",
            message_stream_type=MessageStreamType.BROADCASTS,
            unsubscribe_handling_type=UnsubscribeHandlingType.POSTMARK,
        )

        body = fake.post.call_args[1]["json"]
        assert body["SubscriptionManagementConfiguration"] == {
            "UnsubscribeHandlingType": "Postmark"
        }

    @pytest.mark.asyncio
    async def test_create_custom_unsubscribe_handling(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        await manager.create(
            id="my-stream",
            name="My Stream",
            message_stream_type=MessageStreamType.BROADCASTS,
            unsubscribe_handling_type=UnsubscribeHandlingType.CUSTOM,
        )

        body = fake.post.call_args[1]["json"]
        assert (
            body["SubscriptionManagementConfiguration"]["UnsubscribeHandlingType"]
            == "Custom"
        )

    @pytest.mark.asyncio
    async def test_create_no_optional_fields_in_body(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        await manager.create(
            id="my-stream",
            name="My Stream",
            message_stream_type=MessageStreamType.TRANSACTIONAL,
        )

        body = fake.post.call_args[1]["json"]
        assert "Description" not in body
        assert "SubscriptionManagementConfiguration" not in body


# ---------------------------------------------------------------------------
# Edit message stream
# ---------------------------------------------------------------------------


class TestEditStream:
    @pytest.mark.asyncio
    async def test_edit_name(self, streams):
        manager, fake = streams
        fake.mock_patch_response(_make_stream(Name="Renamed Stream"))

        stream = await manager.edit("outbound", name="Renamed Stream")

        assert stream.name == "Renamed Stream"
        fake.patch.assert_called_once_with(
            "/message-streams/outbound", json={"Name": "Renamed Stream"}
        )

    @pytest.mark.asyncio
    async def test_edit_description(self, streams):
        manager, fake = streams
        fake.mock_patch_response(_make_stream(Description="Updated description"))

        await manager.edit("outbound", description="Updated description")

        body = fake.patch.call_args[1]["json"]
        assert body["Description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_edit_unsubscribe_handling(self, streams):
        manager, fake = streams
        fake.mock_patch_response(
            _make_stream(
                SubscriptionManagementConfiguration={
                    "UnsubscribeHandlingType": "Postmark"
                }
            )
        )

        await manager.edit(
            "outbound", unsubscribe_handling_type=UnsubscribeHandlingType.POSTMARK
        )

        body = fake.patch.call_args[1]["json"]
        assert body["SubscriptionManagementConfiguration"] == {
            "UnsubscribeHandlingType": "Postmark"
        }

    @pytest.mark.asyncio
    async def test_edit_no_args_sends_empty_body(self, streams):
        manager, fake = streams
        fake.mock_patch_response(STREAM)

        await manager.edit("outbound")

        fake.patch.assert_called_once_with("/message-streams/outbound", json={})

    @pytest.mark.asyncio
    async def test_edit_calls_patch_not_put(self, streams):
        manager, fake = streams
        fake.mock_patch_response(STREAM)

        await manager.edit("outbound", name="Test")

        fake.patch.assert_called_once()
        fake.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_edit_multiple_fields(self, streams):
        manager, fake = streams
        fake.mock_patch_response(STREAM)

        await manager.edit(
            "outbound",
            name="New Name",
            description="New description",
            unsubscribe_handling_type=UnsubscribeHandlingType.CUSTOM,
        )

        body = fake.patch.call_args[1]["json"]
        assert body == {
            "Name": "New Name",
            "Description": "New description",
            "SubscriptionManagementConfiguration": {
                "UnsubscribeHandlingType": "Custom"
            },
        }


# ---------------------------------------------------------------------------
# Archive message stream
# ---------------------------------------------------------------------------


class TestArchiveStream:
    ARCHIVE_RESPONSE = {
        "ID": "outbound",
        "ServerID": 23,
        "ExpectedPurgeDate": "2021-03-05T08:00:00-04:00",
    }

    @pytest.mark.asyncio
    async def test_archive_success(self, streams):
        manager, fake = streams
        fake.mock_post_response(self.ARCHIVE_RESPONSE)

        result = await manager.archive("outbound")

        assert result.id == "outbound"
        assert result.server_id == 23
        assert result.expected_purge_date is not None

    @pytest.mark.asyncio
    async def test_archive_calls_correct_endpoint(self, streams):
        manager, fake = streams
        fake.mock_post_response(self.ARCHIVE_RESPONSE)

        await manager.archive("outbound")

        fake.post.assert_called_once_with("/message-streams/outbound/archive")

    @pytest.mark.asyncio
    async def test_archive_different_stream_id(self, streams):
        manager, fake = streams
        fake.mock_post_response({**self.ARCHIVE_RESPONSE, "ID": "broadcasts"})

        await manager.archive("broadcasts")

        fake.post.assert_called_once_with("/message-streams/broadcasts/archive")

    @pytest.mark.asyncio
    async def test_archive_no_purge_date(self, streams):
        manager, fake = streams
        fake.mock_post_response(
            {"ID": "outbound", "ServerID": 23, "ExpectedPurgeDate": None}
        )

        result = await manager.archive("outbound")

        assert result.expected_purge_date is None


# ---------------------------------------------------------------------------
# Unarchive message stream
# ---------------------------------------------------------------------------


class TestUnarchiveStream:
    @pytest.mark.asyncio
    async def test_unarchive_success(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        stream = await manager.unarchive("outbound")

        assert stream.id == "outbound"
        assert stream.archived_at is None

    @pytest.mark.asyncio
    async def test_unarchive_calls_correct_endpoint(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        await manager.unarchive("outbound")

        fake.post.assert_called_once_with("/message-streams/outbound/unarchive")

    @pytest.mark.asyncio
    async def test_unarchive_different_stream_id(self, streams):
        manager, fake = streams
        fake.mock_post_response(_make_stream(ID="broadcasts"))

        await manager.unarchive("broadcasts")

        fake.post.assert_called_once_with("/message-streams/broadcasts/unarchive")

    @pytest.mark.asyncio
    async def test_unarchive_returns_full_stream(self, streams):
        manager, fake = streams
        fake.mock_post_response(STREAM)

        stream = await manager.unarchive("outbound")

        assert stream.server_id == 23
        assert stream.message_stream_type == MessageStreamType.TRANSACTIONAL
        assert (
            stream.subscription_management_configuration.unsubscribe_handling_type
            == UnsubscribeHandlingType.NONE
        )
