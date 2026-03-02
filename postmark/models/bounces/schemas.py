from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .enums import BounceType


class Bounce(BaseModel):
    """A single bounce record returned by the Postmark API"""

    id: int = Field(alias="ID")
    type: BounceType = Field(alias="Type")
    type_code: int = Field(alias="TypeCode")
    name: str = Field(alias="Name")
    tag: Optional[str] = Field(None, alias="Tag")
    message_id: str = Field(alias="MessageID")
    server_id: int = Field(alias="ServerID")
    message_stream: str = Field(alias="MessageStream")
    description: str = Field(alias="Description")
    details: str = Field(alias="Details")
    email: EmailStr = Field(alias="Email")
    sender: str = Field(alias="From")
    bounced_at: datetime = Field(alias="BouncedAt")
    dump_available: bool = Field(alias="DumpAvailable")
    inactive: bool = Field(alias="Inactive")
    can_activate: bool = Field(alias="CanActivate")
    subject: str = Field(alias="Subject")
    content: Optional[str] = Field(None, alias="Content")

    model_config = ConfigDict(populate_by_name=True)


class BounceTypeCount(BaseModel):
    """Aggregate count for a single bounce type, returned within DeliveryStats"""

    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    count: int = Field(alias="Count")
    type_code: int = Field(alias="TypeCode")

    model_config = ConfigDict(populate_by_name=True)


class DeliveryStats(BaseModel):
    """Response from ``GET /deliverystats``"""

    inactive_mails: int = Field(alias="InactiveMails")
    bounces: List[BounceTypeCount] = Field(alias="Bounces")

    model_config = ConfigDict(populate_by_name=True)


class BouncesListResponse(BaseModel):
    """Response from ``GET /bounces``"""

    total_count: int = Field(alias="TotalCount")
    bounces: List[Bounce] = Field(alias="Bounces")

    model_config = ConfigDict(populate_by_name=True)


class BounceDump(BaseModel):
    """
    Response from ``GET /bounces/{bounceid}/dump``.

    ``body`` contains the raw SMTP source.  Returns mpty string if the
    dump is no longer available (Postmark retains dumps for 30 days)
    """

    body: str = Field(alias="Body")

    model_config = ConfigDict(populate_by_name=True)


class ActivateBounceResponse(BaseModel):
    """Response from ``PUT /bounces/{bounceid}/activate``"""

    message: str = Field(alias="Message")
    bounce: Bounce = Field(alias="Bounce")

    model_config = ConfigDict(populate_by_name=True)
