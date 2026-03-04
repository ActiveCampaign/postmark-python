from enum import Enum


class SuppressionReason(str, Enum):
    HARD_BOUNCE = "HardBounce"
    SPAM_COMPLAINT = "SpamComplaint"
    MANUAL_SUPPRESSION = "ManualSuppression"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class SuppressionOrigin(str, Enum):
    RECIPIENT = "Recipient"
    CUSTOMER = "Customer"
    ADMIN = "Admin"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None
