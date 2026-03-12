from enum import Enum


class MessageStreamType(str, Enum):
    """
    Type of a Postmark message stream.
    https://postmarkapp.com/developer/api/message-streams-api
    """

    TRANSACTIONAL = "Transactional"
    BROADCASTS = "Broadcasts"
    INBOUND = "Inbound"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class UnsubscribeHandlingType(str, Enum):
    """
    Unsubscribe handling mode for a message stream.
    https://postmarkapp.com/developer/api/message-streams-api
    """

    NONE = "None"
    POSTMARK = "Postmark"
    CUSTOM = "Custom"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None
