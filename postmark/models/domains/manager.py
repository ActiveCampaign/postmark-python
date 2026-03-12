from typing import Optional

from postmark.models.page import Page
from postmark.utils.types import HTTPClient

from .schemas import (
    DeleteDomainResponse,
    Domain,
    DomainListItem,
    DomainsListResponse,
    SPFVerificationResponse,
)


class DomainManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
    ) -> "Page[DomainListItem]":
        """
        List domains on the account.

        Args:
            count: Number of domains to return per request.
            offset: Number of records to skip.
        """
        response = await self.client.get(
            "/domains", params={"count": count, "offset": offset}
        )
        data = DomainsListResponse(**response.json())
        return Page(items=data.domains, total=data.total_count)

    async def get(self, domain_id: int) -> Domain:
        """Return full details for a domain by ID."""
        response = await self.client.get(f"/domains/{domain_id}")
        return Domain(**response.json())

    async def create(
        self,
        name: str,
        return_path_domain: Optional[str] = None,
    ) -> Domain:
        """
        Create a new domain on the account.

        Args:
            name: Domain name (required).
            return_path_domain: Custom Return-Path domain.
        """
        body: dict = {"Name": name}

        if return_path_domain is not None:
            body["ReturnPathDomain"] = return_path_domain

        response = await self.client.post("/domains", json=body)
        return Domain(**response.json())

    async def edit(
        self,
        domain_id: int,
        return_path_domain: Optional[str] = None,
    ) -> Domain:
        """
        Update a domain.

        Only the fields you provide are changed; omitted fields are left unchanged.

        Args:
            domain_id: ID of the domain to update.
            return_path_domain: Custom Return-Path domain.
        """
        body: dict = {}

        if return_path_domain is not None:
            body["ReturnPathDomain"] = return_path_domain

        response = await self.client.put(f"/domains/{domain_id}", json=body)
        return Domain(**response.json())

    async def delete(self, domain_id: int) -> DeleteDomainResponse:
        """Delete a domain by ID."""
        response = await self.client.delete(f"/domains/{domain_id}")
        return DeleteDomainResponse(**response.json())

    async def verify_dkim(self, domain_id: int) -> Domain:
        """Trigger a DKIM verification check and return the updated domain."""
        response = await self.client.put(f"/domains/{domain_id}/verifyDkim")
        return Domain(**response.json())

    async def verify_return_path(self, domain_id: int) -> Domain:
        """Trigger a Return-Path verification check and return the updated domain."""
        response = await self.client.put(f"/domains/{domain_id}/verifyReturnPath")
        return Domain(**response.json())

    async def verify_spf(self, domain_id: int) -> SPFVerificationResponse:
        """
        Trigger an SPF verification check and return the result.

        .. deprecated::
            Postmark has deprecated SPF verification. Use DKIM instead.
        """
        response = await self.client.post(f"/domains/{domain_id}/verifyspf")
        return SPFVerificationResponse(**response.json())

    async def rotate_dkim(self, domain_id: int) -> Domain:
        """Rotate DKIM keys for the domain and return the updated domain."""
        response = await self.client.post(f"/domains/{domain_id}/rotatedkim")
        return Domain(**response.json())
