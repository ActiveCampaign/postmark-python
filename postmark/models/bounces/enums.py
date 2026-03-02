from enum import Enum


class BounceType(str, Enum):
    """
    Postmark bounce type identifiers used for filtering and classification.
    https://postmarkapp.com/developer/api/bounce-api#bounce-types
    """

    HARD_BOUNCE = "HardBounce"
    """Permanent delivery failure — unknown user or non-existent mailbox."""

    TRANSIENT = "Transient"
    """Temporary delivery failure or network delay."""

    UNSUBSCRIBE = "Unsubscribe"
    """Recipient requested to unsubscribe."""

    SUBSCRIBE = "Subscribe"
    """Recipient requested to subscribe."""

    AUTO_RESPONDER = "AutoResponder"
    """Automatic email response (out-of-office, NDR, etc.)."""

    ADDRESS_CHANGE = "AddressChange"
    """Recipient requested an address change."""

    DNS_ERROR = "DnsError"
    """Temporary DNS resolution error."""

    SPAM_NOTIFICATION = "SpamNotification"
    """Message was blocked or classified as spam by the recipient's provider."""

    OPEN_RELAY_TEST = "OpenRelayTest"
    """Open relay test message — safe to ignore."""

    UNKNOWN = "Unknown"
    """Postmark could not classify this bounce."""

    SOFT_BOUNCE = "SoftBounce"
    """Temporary failure — mailbox full or unavailable."""

    VIRUS_NOTIFICATION = "VirusNotification"
    """Virus warning notification from the receiving server."""

    CHALLENGE_VERIFICATION = "ChallengeVerification"
    """Spam challenge-response verification request."""

    BAD_EMAIL_ADDRESS = "BadEmailAddress"
    """Invalid email address format."""

    SPAM_COMPLAINT = "SpamComplaint"
    """Recipient marked the message as spam."""

    MANUALLY_DEACTIVATED = "ManuallyDeactivated"
    """Address was manually deactivated by an administrator."""

    UNCONFIRMED = "Unconfirmed"
    """Email address confirmation is still pending."""

    BLOCKED = "Blocked"
    """Message blocked by the ISP due to content or blacklisting."""

    SMTP_API_ERROR = "SMTPApiError"
    """SMTP API did not accept the message."""

    INBOUND_ERROR = "InboundError"
    """Inbound message delivery failure."""

    DMARC_POLICY = "DMARCPolicy"
    """Message rejected due to DMARC policy."""

    TEMPLATE_RENDERING_FAILED = "TemplateRenderingFailed"
    """Server-side template rendering error."""
