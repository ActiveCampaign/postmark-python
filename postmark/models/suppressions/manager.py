from datetime import date
from typing import List, Optional

from postmark.utils.types import HTTPClient

from .enums import SuppressionOrigin, SuppressionReason
from .schemas import SuppressionEntry, SuppressionResult


class SuppressionManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def dump(
        self,
        stream_id: str,
        suppression_reason: Optional[SuppressionReason] = None,
        origin: Optional[SuppressionOrigin] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        email_address: Optional[str] = None,
    ) -> List[SuppressionEntry]:
        """
        Return all suppressions for a message stream.

        Args:
            stream_id: Message stream ID (e.g. ``"outbound"``).
            suppression_reason: Filter by reason (see :class:`SuppressionReason`).
            origin: Filter by origin (see :class:`SuppressionOrigin`).
            from_date: Include suppressions created on or after this date.
            to_date: Include suppressions created on or before this date.
            email_address: Filter by specific email address.
        """
        params: dict = {}
        if suppression_reason is not None:
            params["SuppressionReason"] = suppression_reason.value
        if origin is not None:
            params["Origin"] = origin.value
        if from_date is not None:
            params["fromdate"] = from_date.strftime("%Y-%m-%d")
        if to_date is not None:
            params["todate"] = to_date.strftime("%Y-%m-%d")
        if email_address is not None:
            params["EmailAddress"] = email_address

        response = await self.client.get(
            f"/message-streams/{stream_id}/suppressions/dump", params=params
        )
        return [SuppressionEntry(**s) for s in response.json()["Suppressions"]]

    async def create(
        self, stream_id: str, email_addresses: List[str]
    ) -> List[SuppressionResult]:
        """
        Suppress one or more email addresses on a message stream (max 50 per call).

        Args:
            stream_id: Message stream ID.
            email_addresses: List of email addresses to suppress.
        """
        if len(email_addresses) > 50:
            raise ValueError("email_addresses cannot exceed 50 per request.")
        body = {"Suppressions": [{"EmailAddress": e} for e in email_addresses]}
        response = await self.client.post(
            f"/message-streams/{stream_id}/suppressions", json=body
        )
        return [SuppressionResult(**s) for s in response.json()["Suppressions"]]

    async def delete(
        self, stream_id: str, email_addresses: List[str]
    ) -> List[SuppressionResult]:
        """
        Remove suppressions for one or more email addresses (max 50 per call).

        Note: SpamComplaint suppressions cannot be deleted.

        Args:
            stream_id: Message stream ID.
            email_addresses: List of email addresses to unsuppress.
        """
        if len(email_addresses) > 50:
            raise ValueError("email_addresses cannot exceed 50 per request.")
        body = {"Suppressions": [{"EmailAddress": e} for e in email_addresses]}
        response = await self.client.post(
            f"/message-streams/{stream_id}/suppressions/delete", json=body
        )
        return [SuppressionResult(**s) for s in response.json()["Suppressions"]]
