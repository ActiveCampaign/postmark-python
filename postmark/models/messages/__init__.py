from .enums import MessageEventType, MessageStatus, Platform, TrackLinksOption
from .manager import EmailManager
from .schemas import (
    Attachment,
    # Bulk
    BulkEmail,
    BulkRecipient,
    BulkSendResponse,
    BulkSendStatus,
    # Single / batch
    Email,
    EmailAddress,
    Header,
    Message,
    MessageDetails,
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
    # Enums
    "MessageStatus",
    "TrackLinksOption",
    "MessageEventType",
    "Platform",
    # Managers
    "EmailManager",
]
