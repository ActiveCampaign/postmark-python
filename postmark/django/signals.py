"""Signals dispatched by postmark.django.EmailBackend."""

from django.dispatch import Signal

#: Sent just before a batch is submitted to Postmark. kwargs: messages (list[postmark.Email]).
pre_send = Signal()

#: Sent just after a batch is submitted successfully. kwargs: messages, response (list[postmark.SendResponse]).
post_send = Signal()

#: Sent when send_messages() raises. kwargs: raw_messages (the original Django messages), exception.
on_exception = Signal()
