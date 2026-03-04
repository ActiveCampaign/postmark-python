from postmark.models.page import Page
from postmark.utils.types import HTTPClient

from .schemas import DeleteInboundRuleResponse, InboundRule, InboundRulesListResponse


class InboundRuleManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def list(self, count: int = 100, offset: int = 0) -> "Page[InboundRule]":
        """List inbound rule triggers for the server."""
        response = await self.client.get(
            "/triggers/inboundrules", params={"count": count, "offset": offset}
        )
        data = InboundRulesListResponse(**response.json())
        return Page(items=data.inbound_rules, total=data.total_count)

    async def create(self, rule: str) -> InboundRule:
        """
        Create an inbound rule trigger.

        Args:
            rule: Email address or domain to block (e.g. ``"spam@example.com"``
                or ``"example.com"``).
        """
        response = await self.client.post("/triggers/inboundrules", json={"Rule": rule})
        return InboundRule(**response.json())

    async def delete(self, trigger_id: int) -> DeleteInboundRuleResponse:
        """Delete an inbound rule trigger by ID."""
        response = await self.client.delete(f"/triggers/inboundrules/{trigger_id}")
        return DeleteInboundRuleResponse(**response.json())
