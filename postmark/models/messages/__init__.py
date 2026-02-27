from .enums import MessageStatus, TrackLinksOption, MessageEventType, Platform
from .schemas import (
    # Single / batch
    Email,
    SendResponse,
    Outbound,
    OutboundMessageDetails,
    Attachment,
    Header,
    EmailAddress,
    # Bulk
    BulkEmail,
    BulkRecipient,
    BulkSendResponse,
    BulkSendStatus,
)
from .manager import OutboundManager

__all__ = [
    # Schemas — single / batch
    "Email",
    "SendResponse",
    "Outbound",
    "OutboundMessageDetails",
    "Attachment",
    "Header",
    "EmailAddress",
    # Schemas — bulk
    "BulkEmail",
    "BulkRecipient",
    "BulkSendResponse",
    "BulkSendStatus",
    # Enums
    "MessageStatus",
    "TrackLinksOption",
    "MessageEventType",
    "Platform",
    # Managers
    "OutboundManager",
]
