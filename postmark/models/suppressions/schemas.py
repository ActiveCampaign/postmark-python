from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import SuppressionOrigin, SuppressionReason


class SuppressionEntry(BaseModel):
    """A single suppression record returned by the dump endpoint."""

    email_address: str = Field(alias="EmailAddress")
    suppression_reason: SuppressionReason = Field(alias="SuppressionReason")
    origin: SuppressionOrigin = Field(alias="Origin")
    created_at: datetime = Field(alias="CreatedAt")

    model_config = ConfigDict(populate_by_name=True)


class SuppressionResult(BaseModel):
    """Result for a single email address from a create or delete suppression request."""

    email_address: str = Field(alias="EmailAddress")
    status: str = Field(alias="Status")
    message: Optional[str] = Field(None, alias="Message")

    model_config = ConfigDict(populate_by_name=True)
