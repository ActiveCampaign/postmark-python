import logging
import re
from typing import Annotated, Any, Dict, List, Optional, Union


from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    TypeAdapter,
    ValidationError,
)


# Initialize TypeAdapter
email_adapter = TypeAdapter(EmailStr)

# Logging Initialize
logger = logging.getLogger(__name__)


def validate_formatted_email(v: str) -> str:
    """
    Validate email fields that may contain formatted strings like "Name" <email@example.com>
    """

    if v is None:  # None
        raise ValueError("Email cannot be None")
    if not v:  # Empty string
        raise ValueError("Email cannot be empty")

    # Extract email from formats like: "Name" <email@example.com> or just email@example.com
    email_pattern = r'<([^>]+)>|([^\s<>"]+@[^\s<>"]+)'
    match = re.search(email_pattern, v)
    if not match:
        raise ValueError(f"Invalid email field format: {v}")

    email = match.group(1) or match.group(2)
    try:
        # Correct way to validate in Pydantic v2
        email_adapter.validate_python(email)
    except ValidationError:
        raise ValueError(f"Invalid email address: {email}")

    return v


def validate_email_list(v: List[str]) -> List[str]:
    """Validate that all items in a list are valid email addresses"""
    for email in v:
        try:
            email_adapter.validate_python(email)
        except ValidationError:
            raise ValueError(f"Invalid email address in list: {email}")
    return v
