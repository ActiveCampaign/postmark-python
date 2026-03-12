from .enums import MessageEventType, MessageStatus, Platform, TrackLinksOption
from .manager import OutboundManager
from .schemas import (
    Attachment,
    # Bulk
    BulkEmail,
    BulkRecipient,
    BulkSendResponse,
    BulkSendStatus,
    # Single / batch
    ClickEvent,
    Email,
    EmailAddress,
    Header,
    Message,
    MessageDetails,
    OpenEvent,
    OutboundMessageDump,
    SendResponse,
)

__all__ = [
    # Schemas — single / batch
    "Email",
    "SendResponse",
    "Message",
    "MessageDetails",
    "Attachment",
    "Header",
    "EmailAddress",
    # Schemas — bulk
    "BulkEmail",
    "BulkRecipient",
    "BulkSendResponse",
    "BulkSendStatus",
    # Schemas — outbound retrieval
    "OutboundMessageDump",
    "OpenEvent",
    "ClickEvent",
    # Enums
    "MessageStatus",
    "TrackLinksOption",
    "MessageEventType",
    "Platform",
    # Managers
    "OutboundManager",
]
