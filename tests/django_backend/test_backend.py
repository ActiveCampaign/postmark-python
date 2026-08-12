"""Tests for postmark.django.EmailBackend."""

from email.mime.text import MIMEText

import pytest
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.test import override_settings

from postmark.django.backend import TEST_SERVER_TOKEN, EmailBackend
from postmark.django.mixins import PostmarkEmailMessage
from postmark.django.signals import on_exception, post_send, pre_send
from postmark.exceptions import PostmarkAPIException, ValidationException
from postmark.models.outbound.schemas import SendResponse


def test_send_mail_basic(sync_client_factory, fake_sync_client):
    send_mail(
        "Subject here",
        "Here is the message.",
        "sender@example.com",
        ["receiver@example.com"],
    )

    calls = fake_sync_client.outbound.calls
    assert len(calls) == 1
    [email] = calls[0]
    assert email.sender == "sender@example.com"
    assert email.to == "receiver@example.com"
    assert email.subject == "Subject here"
    assert email.text_body == "Here is the message."
    assert email.cc is None
    assert email.bcc is None


def test_cc_bcc_reply_to_together(sync_client_factory, fake_sync_client):
    message = EmailMessage(
        "Subject",
        "Body",
        "sender@example.com",
        ["receiver@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        reply_to=["reply@example.com"],
    )
    message.send()

    [email] = fake_sync_client.outbound.calls[0]
    assert email.cc == "cc@example.com"
    assert email.bcc == "bcc@example.com"
    assert email.reply_to == "reply@example.com"


@pytest.mark.parametrize(
    "field,addresses",
    [
        ("cc", ["cc@example.com"]),
        ("cc", ["cc1@example.com", "cc2@example.com"]),
        ("bcc", ["bcc@example.com"]),
        ("bcc", ["bcc1@example.com", "bcc2@example.com"]),
        ("reply_to", ["reply@example.com"]),
        ("reply_to", ["reply1@example.com", "reply2@example.com"]),
    ],
)
def test_recipient_fields_are_comma_joined(
    sync_client_factory, fake_sync_client, field, addresses
):
    message = EmailMessage(
        "Subject",
        "Body",
        "sender@example.com",
        ["receiver@example.com"],
        **{field: addresses},
    )
    message.send()

    [email] = fake_sync_client.outbound.calls[0]
    assert getattr(email, field) == ", ".join(addresses)


@pytest.mark.parametrize("message_class", [EmailMessage, EmailMultiAlternatives])
def test_basic_send_works_for_all_message_types(
    sync_client_factory, fake_sync_client, message_class
):
    message = message_class(
        "Subject", "Body", "sender@example.com", ["receiver@example.com"]
    )
    message.send()

    [email] = fake_sync_client.outbound.calls[0]
    assert email.subject == "Subject"
    assert email.text_body == "Body"


def test_unicode_subject_and_body_round_trip(sync_client_factory, fake_sync_client):
    """
    Postmark's API is JSON/UTF-8, unlike raw SMTP, so non-ASCII content needs
    no RFC 2047 header encoding — it should pass through unchanged.
    """
    message = EmailMessage(
        "Тест emoji 🎉",
        "Héllo wörld — 日本語のテスト",
        "Тест <sender@example.com>",
        ["Тест <receiver@example.com>"],
    )
    message.send()

    [email] = fake_sync_client.outbound.calls[0]
    assert email.subject == "Тест emoji 🎉"
    assert email.text_body == "Héllo wörld — 日本語のテスト"
    assert email.sender == "Тест <sender@example.com>"
    assert email.to == "Тест <receiver@example.com>"


def test_html_alternative(sync_client_factory, fake_sync_client):
    message = EmailMultiAlternatives(
        "Subject", "text body", "sender@example.com", ["receiver@example.com"]
    )
    message.attach_alternative("<html>hi</html>", "text/html")
    message.send()

    [email] = fake_sync_client.outbound.calls[0]
    assert email.html_body == "<html>hi</html>"
    assert email.text_body == "text body"


def test_unsupported_alternative_mimetype_is_dropped_not_crashed(
    sync_client_factory, fake_sync_client, caplog
):
    message = EmailMultiAlternatives(
        "Subject", "text body", "sender@example.com", ["receiver@example.com"]
    )
    message.attach_alternative('{"not": "html"}', "application/json")

    message.send()  # must not raise

    [email] = fake_sync_client.outbound.calls[0]
    assert email.html_body is None
    assert "application/json" in caplog.text


def test_attachment_is_base64_encoded(sync_client_factory, fake_sync_client):
    message = EmailMessage(
        "Subject", "Body", "sender@example.com", ["receiver@example.com"]
    )
    message.attach("hello.txt", "Hello World", "text/plain")
    message.send()

    [email] = fake_sync_client.outbound.calls[0]
    assert email.attachments[0].name == "hello.txt"
    assert email.attachments[0].content_type == "text/plain"
    assert email.attachments[0].content == "SGVsbG8gV29ybGQ="  # base64("Hello World")


def test_legacy_mimebase_attachment_raises_clear_error(
    sync_client_factory, fake_sync_client
):
    message = EmailMessage(
        "Subject", "Body", "sender@example.com", ["receiver@example.com"]
    )
    mime_part = MIMEText("Hello World", "plain")
    message.attachments.append(mime_part)

    with pytest.raises(TypeError, match="legacy MIMEBase"):
        message.send()


def test_missing_token_raises_improperly_configured():
    with override_settings(POSTMARK_SERVER_TOKEN=None):
        with pytest.raises(ImproperlyConfigured):
            EmailBackend()


def test_server_token_kwarg_overrides_setting(sync_client_factory):
    backend = EmailBackend(server_token="kwarg-token")
    assert backend.server_token == "kwarg-token"


def test_test_mode_uses_test_server_token(sync_client_factory):
    with override_settings(POSTMARK_TEST_MODE=True):
        backend = EmailBackend()
        backend.open()

    (args, _kwargs) = sync_client_factory.calls[0]
    assert args[0] == TEST_SERVER_TOKEN


def test_track_opens_default_from_settings(sync_client_factory, fake_sync_client):
    with override_settings(POSTMARK_TRACK_OPENS=True):
        send_mail("Subject", "Body", "sender@example.com", ["receiver@example.com"])

    [email] = fake_sync_client.outbound.calls[0]
    assert email.track_opens is True


def test_message_stream_default_and_override(sync_client_factory, fake_sync_client):
    with override_settings(POSTMARK_MESSAGE_STREAM="broadcasts"):
        send_mail("Subject", "Body", "sender@example.com", ["receiver@example.com"])
        [default_email] = fake_sync_client.outbound.calls[-1]
        assert default_email.message_stream == "broadcasts"

        PostmarkEmailMessage(
            "Subject",
            "Body",
            "sender@example.com",
            ["receiver@example.com"],
            message_stream="outbound",
        ).send()
        [overridden_email] = fake_sync_client.outbound.calls[-1]
        assert overridden_email.message_stream == "outbound"


def test_tag_and_metadata_via_mixin(sync_client_factory, fake_sync_client):
    PostmarkEmailMessage(
        "Subject",
        "Body",
        "sender@example.com",
        ["receiver@example.com"],
        tag="welcome",
        metadata={"user_id": "42"},
    ).send()

    [email] = fake_sync_client.outbound.calls[0]
    assert email.tag == "welcome"
    assert email.metadata == {"user_id": "42"}


def test_fail_silently_true_swallows_and_counts_only_successes(
    sync_client_factory, fake_sync_client
):
    fake_sync_client.outbound.responses_queue.append(
        [
            SendResponse(
                To="ok@example.com",
                SubmittedAt="2024-01-01T00:00:00",
                MessageID="m1",
                ErrorCode=0,
                Message="OK",
            ),
            SendResponse(
                To="bad@example.com",
                SubmittedAt="2024-01-01T00:00:00",
                MessageID="m2",
                ErrorCode=300,
                Message="Invalid 'To' address",
            ),
        ]
    )

    sent = mail.get_connection(fail_silently=True).send_messages(
        [
            EmailMessage("S", "B", "sender@example.com", ["ok@example.com"]),
            EmailMessage("S", "B", "sender@example.com", ["bad@example.com"]),
        ]
    )

    assert sent == 1


def test_fail_silently_false_raises_typed_exception(
    sync_client_factory, fake_sync_client
):
    fake_sync_client.outbound.responses_queue.append(
        [
            SendResponse(
                To="bad@example.com",
                SubmittedAt="2024-01-01T00:00:00",
                MessageID="m1",
                ErrorCode=300,
                Message="Invalid 'To' address",
            )
        ]
    )

    with pytest.raises(ValidationException):
        send_mail("S", "B", "sender@example.com", ["bad@example.com"])


def test_multiple_failures_raise_generic_exception_with_combined_message(
    sync_client_factory, fake_sync_client
):
    fake_sync_client.outbound.responses_queue.append(
        [
            SendResponse(
                To="a@example.com",
                SubmittedAt="2024-01-01T00:00:00",
                MessageID="m1",
                ErrorCode=300,
                Message="bad a",
            ),
            SendResponse(
                To="b@example.com",
                SubmittedAt="2024-01-01T00:00:00",
                MessageID="m2",
                ErrorCode=300,
                Message="bad b",
            ),
        ]
    )

    with pytest.raises(PostmarkAPIException) as exc_info:
        mail.get_connection().send_messages(
            [
                EmailMessage("S", "B", "sender@example.com", ["a@example.com"]),
                EmailMessage("S", "B", "sender@example.com", ["b@example.com"]),
            ]
        )

    assert "bad a" in str(exc_info.value)
    assert "bad b" in str(exc_info.value)


def test_batches_larger_than_500_are_chunked(sync_client_factory, fake_sync_client):
    messages = [
        EmailMessage("S", "B", "sender@example.com", [f"user{i}@example.com"])
        for i in range(501)
    ]

    sent = mail.get_connection().send_messages(messages)

    assert sent == 501
    assert len(fake_sync_client.outbound.calls) == 2
    assert len(fake_sync_client.outbound.calls[0]) == 500
    assert len(fake_sync_client.outbound.calls[1]) == 1


def test_pre_and_post_send_signals_fire(sync_client_factory, fake_sync_client):
    pre_received = {}
    post_received = {}

    def on_pre(sender, **kwargs):
        pre_received.update(kwargs)

    def on_post(sender, **kwargs):
        post_received.update(kwargs)

    pre_send.connect(on_pre)
    post_send.connect(on_post)
    try:
        send_mail("Subject", "Body", "sender@example.com", ["receiver@example.com"])
    finally:
        pre_send.disconnect(on_pre)
        post_send.disconnect(on_post)

    assert len(pre_received["messages"]) == 1
    assert len(post_received["response"]) == 1


def test_on_exception_signal_fires_with_original_messages(
    sync_client_factory, fake_sync_client
):
    fake_sync_client.outbound.responses_queue.append(
        [
            SendResponse(
                To="bad@example.com",
                SubmittedAt="2024-01-01T00:00:00",
                MessageID="m1",
                ErrorCode=300,
                Message="bad",
            )
        ]
    )
    received = {}

    def handler(sender, **kwargs):
        received.update(kwargs)

    on_exception.connect(handler)
    try:
        send_mail(
            "S", "B", "sender@example.com", ["bad@example.com"], fail_silently=True
        )
    finally:
        on_exception.disconnect(handler)

    assert isinstance(received["exception"], ValidationException)
    assert len(received["raw_messages"]) == 1


def test_never_calls_legacy_message_method(
    monkeypatch, sync_client_factory, fake_sync_client
):
    """
    Regression test: this backend must build the payload from EmailMessage's
    high-level attributes, never from .message(). Django 6.0 changed what
    .message() returns (see the "modern email API" release note), so relying
    on it would be fragile across Django versions.
    """

    def boom(self):
        raise AssertionError(".message() should never be called by postmark.django")

    monkeypatch.setattr(EmailMessage, "message", boom)

    send_mail(
        "Subject", "Body", "sender@example.com", ["receiver@example.com"]
    )  # must not raise


def test_context_manager_reuses_and_closes_connection(
    sync_client_factory, fake_sync_client
):
    with mail.get_connection() as connection:
        EmailMessage(
            "S1", "B1", "sender@example.com", ["a@example.com"], connection=connection
        ).send()
        EmailMessage(
            "S2", "B2", "sender@example.com", ["b@example.com"], connection=connection
        ).send()

    assert len(fake_sync_client.outbound.calls) == 2
    assert fake_sync_client.closed is True
