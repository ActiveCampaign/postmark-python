from typing import Optional

from postmark.models.page import Page
from postmark.utils.types import HTTPClient

from .enums import MessageStreamType, UnsubscribeHandlingType
from .schemas import (
    ArchiveMessageStreamResponse,
    MessageStream,
    MessageStreamListResponse,
)


class StreamManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def list(
        self,
        message_stream_type: Optional[MessageStreamType] = None,
        include_archived: bool = False,
    ) -> Page[MessageStream]:
        """
        List all message streams on the server.

        Args:
            message_stream_type: Filter by stream type (see :class:`MessageStreamType`).
            include_archived: Include archived streams in results.
        """
        params: dict = {"IncludeArchivedStreams": include_archived}
        if message_stream_type is not None:
            params["MessageStreamType"] = message_stream_type.value

        response = await self.client.get("/message-streams", params=params)
        data = MessageStreamListResponse(**response.json())
        return Page(items=data.message_streams, total=data.total_count)

    async def get(self, stream_id: str) -> MessageStream:
        """
        Return a single message stream by ID.
        """
        response = await self.client.get(f"/message-streams/{stream_id}")
        return MessageStream(**response.json())

    async def create(
        self,
        id: str,
        name: str,
        message_stream_type: MessageStreamType,
        description: Optional[str] = None,
        unsubscribe_handling_type: Optional[UnsubscribeHandlingType] = None,
    ) -> MessageStream:
        """
        Create a new message stream.

        Args:
            id: Unique identifier for the stream (e.g. ``"my-broadcasts"``).
            name: Display name for the stream.
            message_stream_type: ``Transactional`` or ``Broadcasts`` (see :class:`MessageStreamType`).
            description: Optional description.
            unsubscribe_handling_type: Unsubscribe handling mode (see :class:`UnsubscribeHandlingType`).
        """
        body: dict = {
            "ID": id,
            "Name": name,
            "MessageStreamType": message_stream_type.value,
        }

        if description is not None:
            body["Description"] = description
        if unsubscribe_handling_type is not None:
            body["SubscriptionManagementConfiguration"] = {
                "UnsubscribeHandlingType": unsubscribe_handling_type.value
            }

        response = await self.client.post("/message-streams", json=body)
        return MessageStream(**response.json())

    async def edit(
        self,
        stream_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        unsubscribe_handling_type: Optional[UnsubscribeHandlingType] = None,
    ) -> MessageStream:
        """
        Update a message stream.

        Only the fields you provide are changed; omitted fields are left
        unchanged.  Returns the full updated stream object.

        Args:
            stream_id: ID of the stream to update.
            name: Updated display name.
            description: Updated description.
            unsubscribe_handling_type: Updated unsubscribe handling mode (see :class:`UnsubscribeHandlingType`).
        """
        body: dict = {}

        if name is not None:
            body["Name"] = name
        if description is not None:
            body["Description"] = description
        if unsubscribe_handling_type is not None:
            body["SubscriptionManagementConfiguration"] = {
                "UnsubscribeHandlingType": unsubscribe_handling_type.value
            }

        response = await self.client.patch(f"/message-streams/{stream_id}", json=body)
        return MessageStream(**response.json())

    async def archive(self, stream_id: str) -> ArchiveMessageStreamResponse:
        """
        Archive a message stream. Archived streams are deleted 45 days after archiving.
        """
        response = await self.client.post(f"/message-streams/{stream_id}/archive")
        return ArchiveMessageStreamResponse(**response.json())

    async def unarchive(self, stream_id: str) -> MessageStream:
        """
        Unarchive a previously archived message stream.
        """
        response = await self.client.post(f"/message-streams/{stream_id}/unarchive")
        return MessageStream(**response.json())
