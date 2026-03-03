from typing import Optional

from postmark.utils.types import HTTPClient

from .enums import ServerColor, TrackLinks
from .schemas import Server


class ServerManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def get(self) -> Server:
        """
        Return configuration for the current server.
        """
        response = await self.client.get("/server")
        return Server(**response.json())

    async def edit(
        self,
        name: Optional[str] = None,
        color: Optional[ServerColor] = None,
        raw_email_enabled: Optional[bool] = None,
        smtp_api_activated: Optional[bool] = None,
        inbound_hook_url: Optional[str] = None,
        bounce_hook_url: Optional[str] = None,
        open_hook_url: Optional[str] = None,
        delivery_hook_url: Optional[str] = None,
        click_hook_url: Optional[str] = None,
        post_first_open_only: Optional[bool] = None,
        track_opens: Optional[bool] = None,
        track_links: Optional[TrackLinks] = None,
        inbound_domain: Optional[str] = None,
        inbound_spam_threshold: Optional[int] = None,
        include_bounce_content_in_hook: Optional[bool] = None,
        enable_smtp_api_error_hooks: Optional[bool] = None,
    ) -> Server:
        """
        Update configuration for the current server.

        Only the fields you provide are changed; omitted fields are left
        unchanged.  Returns the full updated server object.

        Args:
            name: Display name for the server.
            color: Dashboard colour (see :class:`ServerColor`).
            raw_email_enabled: Include raw email in inbound webhook payloads.
            smtp_api_activated: Enable or disable the SMTP API.
            inbound_hook_url: Webhook URL for inbound messages.
            bounce_hook_url: Webhook URL for bounce events.
            open_hook_url: Webhook URL for open-tracking events.
            delivery_hook_url: Webhook URL for delivery confirmations.
            click_hook_url: Webhook URL for click-tracking events.
            post_first_open_only: Fire the open webhook only on the first open.
            track_opens: Enable open tracking.
            track_links: Link-tracking scope (see :class:`TrackLinks`).
            inbound_domain: Domain used for MX-based inbound routing.
            inbound_spam_threshold: Maximum spam score before blocking inbound mail.
            include_bounce_content_in_hook: Attach bounce content to webhook payloads.
            enable_smtp_api_error_hooks: Include SMTP API errors in bounce webhooks.
        """
        body: dict = {}

        if name is not None:
            body["Name"] = name
        if color is not None:
            body["Color"] = color.value
        if raw_email_enabled is not None:
            body["RawEmailEnabled"] = raw_email_enabled
        if smtp_api_activated is not None:
            body["SmtpApiActivated"] = smtp_api_activated
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
        if track_opens is not None:
            body["TrackOpens"] = track_opens
        if track_links is not None:
            body["TrackLinks"] = track_links.value
        if inbound_domain is not None:
            body["InboundDomain"] = inbound_domain
        if inbound_spam_threshold is not None:
            body["InboundSpamThreshold"] = inbound_spam_threshold
        if include_bounce_content_in_hook is not None:
            body["IncludeBounceContentInHook"] = include_bounce_content_in_hook
        if enable_smtp_api_error_hooks is not None:
            body["EnableSmtpApiErrorHooks"] = enable_smtp_api_error_hooks

        response = await self.client.put("/server", json=body)
        return Server(**response.json())
