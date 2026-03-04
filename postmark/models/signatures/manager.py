from typing import Optional

from postmark.models.page import Page
from postmark.utils.types import HTTPClient

from .schemas import (
    DeleteSignatureResponse,
    RequestNewDKIMResponse,
    ResendConfirmationResponse,
    SenderSignature,
    SenderSignatureListItem,
    SenderSignaturesListResponse,
)


class SenderSignatureManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
    ) -> "Page[SenderSignatureListItem]":
        """
        List sender signatures on the account.

        Args:
            count: Number of signatures to return per request.
            offset: Number of records to skip.
        """
        response = await self.client.get(
            "/senders", params={"count": count, "offset": offset}
        )
        data = SenderSignaturesListResponse(**response.json())
        return Page(items=data.sender_signatures, total=data.total_count)

    async def get(self, signature_id: int) -> SenderSignature:
        """Return full details for a sender signature by ID."""
        response = await self.client.get(f"/senders/{signature_id}")
        return SenderSignature(**response.json())

    async def create(
        self,
        sender: str,
        name: str,
        reply_to: Optional[str] = None,
        return_path_domain: Optional[str] = None,
        confirmation_personal_note: Optional[str] = None,
    ) -> SenderSignature:
        """
        Create a new sender signature.

        Args:
            sender: Email address to send from (required).
            name: Display name for the sender (required).
            reply_to: Reply-To email address.
            return_path_domain: Custom Return-Path domain.
            confirmation_personal_note: Personal note included in the confirmation
                email (max 400 characters).
        """
        body: dict = {"FromEmail": sender, "Name": name}

        if reply_to is not None:
            body["ReplyToEmail"] = reply_to
        if return_path_domain is not None:
            body["ReturnPathDomain"] = return_path_domain
        if confirmation_personal_note is not None:
            body["ConfirmationPersonalNote"] = confirmation_personal_note

        response = await self.client.post("/senders", json=body)
        return SenderSignature(**response.json())

    async def edit(
        self,
        signature_id: int,
        name: str,
        reply_to: Optional[str] = None,
        return_path_domain: Optional[str] = None,
        confirmation_personal_note: Optional[str] = None,
    ) -> SenderSignature:
        """
        Update a sender signature.

        Args:
            signature_id: ID of the signature to update.
            name: Display name for the sender (required).
            reply_to: Reply-To email address.
            return_path_domain: Custom Return-Path domain.
            confirmation_personal_note: Personal note included in the confirmation
                email (max 400 characters).
        """
        body: dict = {"Name": name}

        if reply_to is not None:
            body["ReplyToEmail"] = reply_to
        if return_path_domain is not None:
            body["ReturnPathDomain"] = return_path_domain
        if confirmation_personal_note is not None:
            body["ConfirmationPersonalNote"] = confirmation_personal_note

        response = await self.client.put(f"/senders/{signature_id}", json=body)
        return SenderSignature(**response.json())

    async def delete(self, signature_id: int) -> DeleteSignatureResponse:
        """Delete a sender signature by ID."""
        response = await self.client.delete(f"/senders/{signature_id}")
        return DeleteSignatureResponse(**response.json())

    async def resend_confirmation(
        self, signature_id: int
    ) -> ResendConfirmationResponse:
        """Resend the confirmation email for a sender signature."""
        response = await self.client.post(f"/senders/{signature_id}/resend")
        return ResendConfirmationResponse(**response.json())

    async def verify_spf(self, signature_id: int) -> SenderSignature:
        """
        Trigger an SPF verification check and return the updated signature.

        .. deprecated::
            Postmark has deprecated SPF verification. Use DKIM instead.
        """
        response = await self.client.post(f"/senders/{signature_id}/verifyspf")
        return SenderSignature(**response.json())

    async def request_new_dkim(self, signature_id: int) -> RequestNewDKIMResponse:
        """
        Request a new DKIM key for the sender signature.

        .. deprecated::
            Postmark has deprecated this endpoint.
        """
        response = await self.client.post(f"/senders/{signature_id}/requestnewdkim")
        return RequestNewDKIMResponse(**response.json())
