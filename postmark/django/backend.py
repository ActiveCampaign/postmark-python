"""
Django email backend for Postmark.

    EMAIL_BACKEND = "postmark.django.EmailBackend"
    POSTMARK_SERVER_TOKEN = "..."

Builds the Postmark payload from Django's high-level EmailMessage /
EmailMultiAlternatives attributes (to, cc, bcc, subject, body, alternatives,
attachments, extra_headers) rather than from EmailMessage.message(). Django 6.0
changed message() to return a Python email.message.EmailMessage instead of the
legacy SafeMIMEText/SafeMIMEMultipart classes, which broke third-party backends
that introspected that MIME object directly — this backend never does that, so
it isn't affected.
"""

import base64
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

from postmark.exceptions import PostmarkAPIException, get_exception_class
from postmark.models.outbound.schemas import Email
from postmark.sync import ServerClient as SyncServerClient

from .signals import on_exception, post_send, pre_send

logger = logging.getLogger(__name__)

# Postmark's own publicly documented token for validating requests without
# delivering mail — not a secret. https://postmarkapp.com/developer/api/overview
TEST_SERVER_TOKEN = "POSTMARK_API_TEST"  # nosec B105

_BATCH_LIMIT = 500


class EmailBackend(BaseEmailBackend):
    """Sends Django email through the Postmark API."""

    def __init__(self, server_token=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.server_token = server_token or getattr(
            settings, "POSTMARK_SERVER_TOKEN", None
        )
        if not self.server_token:
            raise ImproperlyConfigured(
                "Set POSTMARK_SERVER_TOKEN in settings, or pass "
                "server_token= when constructing the Postmark email backend."
            )
        self.test_mode = getattr(settings, "POSTMARK_TEST_MODE", False)
        self.default_track_opens = getattr(settings, "POSTMARK_TRACK_OPENS", None)
        self.default_message_stream = getattr(settings, "POSTMARK_MESSAGE_STREAM", None)
        self._client_kwargs = kwargs
        self.client = None

    def open(self) -> bool:
        """Create the underlying client if one doesn't exist. Returns True if created."""
        if self.client is not None:
            return False
        token = TEST_SERVER_TOKEN if self.test_mode else self.server_token
        self.client = SyncServerClient(token, **self._client_kwargs)
        return True

    def close(self) -> None:
        if self.client is None:
            return
        try:
            self.client.close()
        finally:
            self.client = None

    def send_messages(self, email_messages) -> int:
        if not email_messages:
            return 0

        emails = [self._build_email(message) for message in email_messages]

        sent_count = 0
        try:
            client_created = self.open()
            for start in range(0, len(emails), _BATCH_LIMIT):
                chunk = emails[start : start + _BATCH_LIMIT]
                pre_send.send_robust(self.__class__, messages=chunk)
                responses = self.client.outbound.send_batch(chunk)
                post_send.send_robust(
                    self.__class__, messages=chunk, response=responses
                )
                failures = [r for r in responses if not r.success]
                sent_count += len(responses) - len(failures)
                if failures:
                    self._raise_for_failures(failures)
            if client_created:
                self.close()
        except Exception as exc:
            on_exception.send_robust(
                self.__class__, raw_messages=email_messages, exception=exc
            )
            if not self.fail_silently:
                raise
        return sent_count

    @staticmethod
    def _raise_for_failures(failures) -> None:
        """Raise a typed exception for one or more failed items in a send_batch response."""
        if len(failures) == 1:
            response = failures[0]
            exception_class = get_exception_class(response.error_code, 200)
            raise exception_class(response.message, response.error_code, 200)
        summary = "; ".join(f"[{r.error_code}] {r.message}" for r in failures)
        raise PostmarkAPIException(summary, failures[0].error_code, 200)

    def _build_email(self, message) -> Email:
        """Convert a Django EmailMessage/EmailMultiAlternatives into a postmark.Email."""
        html_body = None
        for content, mimetype in getattr(message, "alternatives", []):
            if mimetype == "text/html":
                html_body = content
            else:
                logger.warning(
                    "postmark.django: dropping unsupported alternative content "
                    "type %r (Postmark's Email API supports a single HTML body)",
                    mimetype,
                )

        track_opens = getattr(message, "track_opens", None)
        if track_opens is None:
            track_opens = self.default_track_opens

        message_stream = getattr(message, "message_stream", None)
        if message_stream is None:
            message_stream = self.default_message_stream

        return Email.model_validate(
            {
                "sender": message.from_email,
                "to": ", ".join(message.to),
                "cc": ", ".join(message.cc) or None,
                "bcc": ", ".join(message.bcc) or None,
                "reply_to": ", ".join(message.reply_to) or None,
                "subject": message.subject,
                "text_body": message.body,
                "html_body": html_body,
                "headers": [
                    {"name": name, "value": value}
                    for name, value in message.extra_headers.items()
                ],
                "attachments": [
                    self._build_attachment(attachment)
                    for attachment in message.attachments
                ],
                "tag": getattr(message, "tag", None),
                "metadata": getattr(message, "metadata", None) or {},
                "message_stream": message_stream,
                "track_opens": track_opens,
            }
        )

    @staticmethod
    def _build_attachment(attachment) -> dict[str, str]:
        if not isinstance(attachment, tuple):
            raise TypeError(
                "postmark.django does not support legacy MIMEBase attachments; "
                "use EmailMessage.attach(filename, content, mimetype) instead."
            )
        filename, content, mimetype = attachment
        content_bytes = content.encode("utf-8") if isinstance(content, str) else content
        return {
            "name": filename or "",
            "content": base64.b64encode(content_bytes).decode("ascii"),
            "content_type": mimetype or "application/octet-stream",
        }
