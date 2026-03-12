from enum import Enum


class ServerColor(str, Enum):
    """
    Display colour options for a Postmark server.
    https://postmarkapp.com/developer/api/server-api#edit-server
    """

    PURPLE = "Purple"
    BLUE = "Blue"
    TURQUOISE = "Turquoise"
    GREEN = "Green"
    RED = "Red"
    YELLOW = "Yellow"
    GREY = "Grey"
    ORANGE = "Orange"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class TrackLinks(str, Enum):
    """
    Link-tracking scope for outbound messages.
    https://postmarkapp.com/developer/api/server-api#edit-server
    """

    NONE = "None"
    """No link tracking."""

    HTML_AND_TEXT = "HtmlAndText"
    """Track links in both HTML and plain-text parts."""

    HTML_ONLY = "HtmlOnly"
    """Track links in the HTML part only."""

    TEXT_ONLY = "TextOnly"
    """Track links in the plain-text part only."""

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class DeliveryType(str, Enum):
    """
    Environment type reported by the Postmark API.
    https://postmarkapp.com/developer/api/server-api#get-server
    """

    LIVE = "Live"
    SANDBOX = "Sandbox"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None
