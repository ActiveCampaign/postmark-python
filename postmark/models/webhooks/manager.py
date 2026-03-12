from typing import Dict, List, Optional

from postmark.utils.types import HTTPClient

from .schemas import DeleteWebhookResponse, Webhook, WebhooksListResponse


class WebhookManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def list(self, message_stream: Optional[str] = None) -> List[Webhook]:
        """List all webhooks on the server, optionally filtered by message stream."""
        params: dict = {}
        if message_stream is not None:
            params["MessageStream"] = message_stream

        response = await self.client.get("/webhooks", params=params)
        return WebhooksListResponse(**response.json()).webhooks

    async def get(self, webhook_id: int) -> Webhook:
        """Return a single webhook by ID."""
        response = await self.client.get(f"/webhooks/{webhook_id}")
        return Webhook(**response.json())

    async def create(
        self,
        url: str,
        message_stream: Optional[str] = None,
        http_auth: Optional[Dict] = None,
        http_headers: Optional[List[Dict]] = None,
        triggers: Optional[Dict] = None,
    ) -> Webhook:
        """
        Create a webhook.

        Args:
            url: Destination URL for webhook payloads.
            message_stream: Stream to attach to; defaults to ``outbound``.
            http_auth: Basic auth credentials, e.g.
                ``{"Username": "user", "Password": "pass"}``.
            http_headers: Custom headers, e.g.
                ``[{"Name": "X-Custom", "Value": "val"}]``.
            triggers: Trigger configuration using Postmark's PascalCase keys, e.g.
                ``{"Open": {"Enabled": True, "PostFirstOpenOnly": False}}``.
        """
        body: dict = {"Url": url}

        if message_stream is not None:
            body["MessageStream"] = message_stream
        if http_auth is not None:
            body["HttpAuth"] = http_auth
        if http_headers is not None:
            body["HttpHeaders"] = http_headers
        if triggers is not None:
            body["Triggers"] = triggers

        response = await self.client.post("/webhooks", json=body)
        return Webhook(**response.json())

    async def edit(
        self,
        webhook_id: int,
        url: Optional[str] = None,
        http_auth: Optional[Dict] = None,
        http_headers: Optional[List[Dict]] = None,
        triggers: Optional[Dict] = None,
    ) -> Webhook:
        """
        Update a webhook.

        Only fields you provide are changed; omitted fields are left unchanged.

        Args:
            webhook_id: ID of the webhook to update.
            url: New destination URL.
            http_auth: Basic auth credentials dict.
            http_headers: Custom headers list.
            triggers: Trigger configuration dict.
        """
        body: dict = {}

        if url is not None:
            body["Url"] = url
        if http_auth is not None:
            body["HttpAuth"] = http_auth
        if http_headers is not None:
            body["HttpHeaders"] = http_headers
        if triggers is not None:
            body["Triggers"] = triggers

        response = await self.client.put(f"/webhooks/{webhook_id}", json=body)
        return Webhook(**response.json())

    async def delete(self, webhook_id: int) -> DeleteWebhookResponse:
        """Delete a webhook by ID."""
        response = await self.client.delete(f"/webhooks/{webhook_id}")
        return DeleteWebhookResponse(**response.json())
