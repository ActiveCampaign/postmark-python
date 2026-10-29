import builtins

from postmark.utils.types import HTTPClient

from .schemas import (
    DeleteWebhookResponse,
    Webhook,
    WebhooksListResponse,
    WebhookStatistics,
    WebhookVerificationResult,
)


class WebhookManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def list(self, message_stream: str | None = None) -> list[Webhook]:
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
        message_stream: str | None = None,
        http_auth: dict | None = None,
        http_headers: builtins.list[dict] | None = None,
        triggers: dict | None = None,
        verify: bool = True,
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
            verify: By default Postmark sends a test event for every enabled trigger
                and refuses to save the webhook if they fail. ``False`` saves it
                anyway, with each trigger's status ``"unverified"``; use
                :meth:`verify` to verify it later.
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

        endpoint = "/webhooks" if verify else "/webhooks?verify=false"
        response = await self.client.post(endpoint, json=body)
        return Webhook(**response.json())

    async def edit(
        self,
        webhook_id: int,
        url: str | None = None,
        http_auth: dict | None = None,
        http_headers: builtins.list[dict] | None = None,
        triggers: dict | None = None,
        verify: bool = True,
    ) -> Webhook:
        """
        Update a webhook.

        Only fields you provide are changed; omitted fields keep their current value.

        Postmark's ``PUT /webhooks/{id}`` always requires ``Url`` and verifies the
        endpoint using only what the request contains, so this method first reads
        the current webhook, merges your changes into it and sends the complete
        configuration. That costs one extra ``GET`` and is not atomic if the
        webhook is changed elsewhere at the same time.

        Args:
            webhook_id: ID of the webhook to update.
            url: New destination URL.
            http_auth: Basic auth credentials dict (replaces the stored credentials).
            http_headers: Custom headers list (replaces the stored list; ``[]`` clears).
            triggers: Trigger configuration. Merged field by field into the existing
                triggers, so ``{"Bounce": {"Enabled": False}}`` leaves every other
                trigger and every other Bounce setting as it is.
            verify: ``False`` saves the changes without first sending test events
                (see :meth:`create`). Triggers then report ``"unverified"``.
        """
        current = (await self.client.get(f"/webhooks/{webhook_id}")).json()

        body: dict = {"Url": url if url is not None else current["Url"]}

        auth = http_auth if http_auth is not None else current.get("HttpAuth")
        if auth is not None:
            body["HttpAuth"] = auth

        headers = (
            http_headers if http_headers is not None else current.get("HttpHeaders")
        )
        if headers is not None:
            body["HttpHeaders"] = headers

        # Responses carry a read-only per-trigger "Status"; it must not be sent back.
        merged: dict = {
            name: {k: v for k, v in config.items() if k != "Status"}
            for name, config in (current.get("Triggers") or {}).items()
        }
        for name, config in (triggers or {}).items():
            merged[name] = {**merged.get(name, {}), **config}
        if merged:
            body["Triggers"] = merged

        suffix = "" if verify else "?verify=false"
        response = await self.client.put(f"/webhooks/{webhook_id}{suffix}", json=body)
        return Webhook(**response.json())

    async def get_statistics(self, webhook_id: int) -> WebhookStatistics:
        """
        Return delivery statistics for a webhook over the last 24 hours.

        Includes overall and per-trigger request, success, failure and retry counts,
        the success rate and average response times, plus each enabled trigger's
        verification status. The window is fixed by Postmark; there are no filters.
        """
        response = await self.client.get(f"/webhooks/{webhook_id}/statistics")
        return WebhookStatistics(**response.json())

    async def verify(self, webhook_id: int) -> WebhookVerificationResult:
        """
        Send a test event for every enabled trigger to the webhook's URL.

        A failed verification is **not** an error: Postmark answers HTTP 200 with
        ``success=False`` and a per-trigger breakdown (``results``), including the
        status code your endpoint returned (``0`` if it could not be reached). Check
        ``result.success``.

        Each call sends real test requests to your endpoint. Like every call, this
        one is retried automatically on timeouts and 5xx responses, which would send
        the test events again, so give a slow endpoint a generous ``timeout`` on the
        client (the default is 5 seconds).
        """
        response = await self.client.post(f"/webhooks/{webhook_id}/verify")
        return WebhookVerificationResult(**response.json())

    async def delete(self, webhook_id: int) -> DeleteWebhookResponse:
        """Delete a webhook by ID."""
        response = await self.client.delete(f"/webhooks/{webhook_id}")
        return DeleteWebhookResponse(**response.json())
