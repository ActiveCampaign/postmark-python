from typing import Optional

from postmark.models.page import Page
from postmark.utils.types import HTTPClient

from .enums import DeliveryType, ServerColor, TrackLinks
from .schemas import DeleteServerResponse, Server, ServersListResponse


class AccountServerManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def get(self, server_id: int) -> Server:
        """
        Return configuration for a single server by ID.
        """
        response = await self.client.get(f"/servers/{server_id}")
        return Server(**response.json())

    async def create(
        self,
        name: str,
        color: Optional[ServerColor] = None,
        smtp_api_activated: Optional[bool] = None,
        raw_email_enabled: Optional[bool] = None,
        delivery_type: Optional[DeliveryType] = None,
        inbound_hook_url: Optional[str] = None,
        bounce_hook_url: Optional[str] = None,
        open_hook_url: Optional[str] = None,
        delivery_hook_url: Optional[str] = None,
        click_hook_url: Optional[str] = None,
        post_first_open_only: Optional[bool] = None,
        inbound_domain: Optional[str] = None,
        inbound_spam_threshold: Optional[int] = None,
        track_opens: Optional[bool] = None,
        track_links: Optional[TrackLinks] = None,
        include_bounce_content_in_hook: Optional[bool] = None,
        enable_smtp_api_error_hooks: Optional[bool] = None,
    ) -> Server:
        """
        Create a new server on the account.

        Args:
            name: Display name for the server (required).
            color: Dashboard colour (see :class:`ServerColor`).
            smtp_api_activated: Enable or disable the SMTP API.
            raw_email_enabled: Include raw email in inbound webhook payloads.
            delivery_type: ``Live`` or ``Sandbox`` — cannot be changed after creation.
            inbound_hook_url: Webhook URL for inbound messages.
            bounce_hook_url: Webhook URL for bounce events.
            open_hook_url: Webhook URL for open-tracking events.
            delivery_hook_url: Webhook URL for delivery confirmations.
            click_hook_url: Webhook URL for click-tracking events.
            post_first_open_only: Fire the open webhook only on the first open.
            inbound_domain: Domain used for MX-based inbound routing.
            inbound_spam_threshold: Maximum spam score before blocking inbound mail.
            track_opens: Enable open tracking.
            track_links: Link-tracking scope (see :class:`TrackLinks`).
            include_bounce_content_in_hook: Attach bounce content to webhook payloads.
            enable_smtp_api_error_hooks: Include SMTP errors in bounce webhooks.
        """
        body: dict = {"Name": name}

        if color is not None:
            body["Color"] = color.value
        if smtp_api_activated is not None:
            body["SmtpApiActivated"] = smtp_api_activated
        if raw_email_enabled is not None:
            body["RawEmailEnabled"] = raw_email_enabled
        if delivery_type is not None:
            body["DeliveryType"] = delivery_type.value
        if inbound_hook_url is not None:
            body["InboundHookUrl"] = inbound_hook_url
        if bounce_hook_url is not None:
            body["BounceHookUrl"] = bounce_hook_url
        if open_hook_url is not None:
            body["OpenHookUrl"] = open_hook_url
        if delivery_hook_url is not None:
            body["DeliveryHookUrl"] = delivery_hook_url
        if click_hook_url is not None:
            body["ClickHookUrl"] = click_hook_url
        if post_first_open_only is not None:
            body["PostFirstOpenOnly"] = post_first_open_only
        if inbound_domain is not None:
            body["InboundDomain"] = inbound_domain
        if inbound_spam_threshold is not None:
            body["InboundSpamThreshold"] = inbound_spam_threshold
        if track_opens is not None:
            body["TrackOpens"] = track_opens
        if track_links is not None:
            body["TrackLinks"] = track_links.value
        if include_bounce_content_in_hook is not None:
            body["IncludeBounceContentInHook"] = include_bounce_content_in_hook
        if enable_smtp_api_error_hooks is not None:
            body["EnableSmtpApiErrorHooks"] = enable_smtp_api_error_hooks

        response = await self.client.post("/servers", json=body)
        return Server(**response.json())

    async def edit(
        self,
        server_id: int,
        name: Optional[str] = None,
        color: Optional[ServerColor] = None,
        smtp_api_activated: Optional[bool] = None,
        raw_email_enabled: Optional[bool] = None,
        inbound_hook_url: Optional[str] = None,
        bounce_hook_url: Optional[str] = None,
        open_hook_url: Optional[str] = None,
        delivery_hook_url: Optional[str] = None,
        click_hook_url: Optional[str] = None,
        post_first_open_only: Optional[bool] = None,
        inbound_domain: Optional[str] = None,
        inbound_spam_threshold: Optional[int] = None,
        track_opens: Optional[bool] = None,
        track_links: Optional[TrackLinks] = None,
        include_bounce_content_in_hook: Optional[bool] = None,
        enable_smtp_api_error_hooks: Optional[bool] = None,
    ) -> Server:
        """
        Update configuration for a server.

        Only the fields you provide are changed; omitted fields are left
        unchanged.  ``delivery_type`` cannot be changed after creation.

        Args:
            server_id: ID of the server to update.
            name: Display name for the server.
            color: Dashboard colour (see :class:`ServerColor`).
            smtp_api_activated: Enable or disable the SMTP API.
            raw_email_enabled: Include raw email in inbound webhook payloads.
            inbound_hook_url: Webhook URL for inbound messages.
            bounce_hook_url: Webhook URL for bounce events.
            open_hook_url: Webhook URL for open-tracking events.
            delivery_hook_url: Webhook URL for delivery confirmations.
            click_hook_url: Webhook URL for click-tracking events.
            post_first_open_only: Fire the open webhook only on the first open.
            inbound_domain: Domain used for MX-based inbound routing.
            inbound_spam_threshold: Maximum spam score before blocking inbound mail.
            track_opens: Enable open tracking.
            track_links: Link-tracking scope (see :class:`TrackLinks`).
            include_bounce_content_in_hook: Attach bounce content to webhook payloads.
            enable_smtp_api_error_hooks: Include SMTP errors in bounce webhooks.
        """
        body: dict = {}

        if name is not None:
            body["Name"] = name
        if color is not None:
            body["Color"] = color.value
        if smtp_api_activated is not None:
            body["SmtpApiActivated"] = smtp_api_activated
        if raw_email_enabled is not None:
            body["RawEmailEnabled"] = raw_email_enabled
        if inbound_hook_url is not None:
            body["InboundHookUrl"] = inbound_hook_url
        if bounce_hook_url is not None:
            body["BounceHookUrl"] = bounce_hook_url
        if open_hook_url is not None:
            body["OpenHookUrl"] = open_hook_url
        if delivery_hook_url is not None:
            body["DeliveryHookUrl"] = delivery_hook_url
        if click_hook_url is not None:
            body["ClickHookUrl"] = click_hook_url
        if post_first_open_only is not None:
            body["PostFirstOpenOnly"] = post_first_open_only
        if inbound_domain is not None:
            body["InboundDomain"] = inbound_domain
        if inbound_spam_threshold is not None:
            body["InboundSpamThreshold"] = inbound_spam_threshold
        if track_opens is not None:
            body["TrackOpens"] = track_opens
        if track_links is not None:
            body["TrackLinks"] = track_links.value
        if include_bounce_content_in_hook is not None:
            body["IncludeBounceContentInHook"] = include_bounce_content_in_hook
        if enable_smtp_api_error_hooks is not None:
            body["EnableSmtpApiErrorHooks"] = enable_smtp_api_error_hooks

        response = await self.client.put(f"/servers/{server_id}", json=body)
        return Server(**response.json())

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
        name: Optional[str] = None,
    ) -> Page[Server]:
        """
        List servers on the account.

        Args:
            count: Number of servers to return per request.
            offset: Number of records to skip.
            name: Filter by server name (partial match).
        """
        params: dict = {"count": count, "offset": offset}
        if name is not None:
            params["name"] = name

        response = await self.client.get("/servers", params=params)
        data = ServersListResponse(**response.json())
        return Page(items=data.servers, total=data.total_count)

    async def delete(self, server_id: int) -> DeleteServerResponse:
        """
        Delete a server by ID.

        Note: This feature is not enabled for all accounts. Contact Postmark
        support if you receive a permissions error.
        """
        response = await self.client.delete(f"/servers/{server_id}")
        return DeleteServerResponse(**response.json())
