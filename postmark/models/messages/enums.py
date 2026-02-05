from enum import Enum


class MessageStatus(str, Enum):
    SENT = "Sent"
    PROCESSED = "Processed"
    QUEUED = "Queued"
    BLOCKED = "Blocked"
    FAILED = "Failed"
    SCHEDULED = "Scheduled"


class TrackLinksOption(str, Enum):
    NONE = "None"
    HTML_AND_TEXT = "HtmlAndText"
    HTML_ONLY = "HtmlOnly"
    TEXT_ONLY = "TextOnly"


class MessageEventType(str, Enum):
    DELIVERED = "Delivered"
    TRANSIENT = "Transient"
    OPENED = "Opened"
    BOUNCED = "Bounced"
    SUBSCRIPTION_CHANGED = "SubscriptionChanged"
    LINK_CLICKED = "LinkClicked"


class Platform(str, Enum):
    WEBMAIL = "WebMail"
    DESKTOP = "Desktop"
    MOBILE = "Mobile"
    UNKNOWN = "Unknown"
