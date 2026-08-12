"""Tests for postmark.django.mixins."""

from django.core.mail import EmailMessage, EmailMultiAlternatives

from postmark.django.mixins import PostmarkEmailMessage, PostmarkEmailMultiAlternatives


def test_postmark_email_message_defaults_to_none():
    message = PostmarkEmailMessage(
        "Subject", "Body", "sender@example.com", ["r@example.com"]
    )

    assert message.tag is None
    assert message.metadata is None
    assert message.message_stream is None
    assert isinstance(message, EmailMessage)


def test_postmark_email_message_accepts_postmark_fields():
    message = PostmarkEmailMessage(
        "Subject",
        "Body",
        "sender@example.com",
        ["r@example.com"],
        tag="welcome",
        metadata={"k": "v"},
        message_stream="outbound",
    )

    assert message.tag == "welcome"
    assert message.metadata == {"k": "v"}
    assert message.message_stream == "outbound"


def test_postmark_email_multi_alternatives_is_still_a_multi_alternatives():
    message = PostmarkEmailMultiAlternatives(
        "Subject", "text", "sender@example.com", ["r@example.com"], tag="t"
    )
    message.attach_alternative("<p>hi</p>", "text/html")

    assert isinstance(message, EmailMultiAlternatives)
    assert message.tag == "t"
    assert message.alternatives == [("<p>hi</p>", "text/html")]
