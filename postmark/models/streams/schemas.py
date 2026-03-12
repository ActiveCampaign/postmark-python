from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import MessageStreamType, UnsubscribeHandlingType


class SubscriptionManagementConfiguration(BaseModel):
    unsubscribe_handling_type: UnsubscribeHandlingType = Field(
        alias="UnsubscribeHandlingType"
    )

    model_config = ConfigDict(populate_by_name=True)


class MessageStream(BaseModel):
    """A single message stream returned by the Postmark API."""

    id: str = Field(alias="ID")
    server_id: int = Field(alias="ServerID")
    name: str = Field(alias="Name")
    description: Optional[str] = Field(None, alias="Description")
    message_stream_type: MessageStreamType = Field(alias="MessageStreamType")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")
    archived_at: Optional[datetime] = Field(None, alias="ArchivedAt")
    expected_purge_date: Optional[datetime] = Field(None, alias="ExpectedPurgeDate")
    subscription_management_configuration: SubscriptionManagementConfiguration = Field(
        alias="SubscriptionManagementConfiguration"
    )

    model_config = ConfigDict(populate_by_name=True)


class MessageStreamListResponse(BaseModel):
    """Response from ``GET /message-streams``."""

    total_count: int = Field(alias="TotalCount")
    message_streams: List[MessageStream] = Field(alias="MessageStreams")

    model_config = ConfigDict(populate_by_name=True)


class ArchiveMessageStreamResponse(BaseModel):
    """Response from ``POST /message-streams/{stream_ID}/archive``."""

    id: str = Field(alias="ID")
    server_id: int = Field(alias="ServerID")
    expected_purge_date: Optional[datetime] = Field(None, alias="ExpectedPurgeDate")

    model_config = ConfigDict(populate_by_name=True)
