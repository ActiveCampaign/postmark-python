from .enums import MessageStatus, TrackLinksOption, MessageEventType, Platform
from .schemas import (
    # Single / batch
    Email,
    SendResponse,
    Message,
    MessageDetails,
    Attachment,
    Header,
    EmailAddress,
    # Bulk
    BulkEmail,
    BulkRecipient,
    BulkSendResponse,
    BulkSendStatus,
)
from .manager import EmailManager

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
