"""Django email classes that carry Postmark-specific fields (tag, metadata, message stream)."""

from django.core.mail import EmailMessage, EmailMultiAlternatives


class PostmarkEmailMixin:
    """Adds Postmark's tag/metadata/message_stream fields to a Django email class."""

    def __init__(self, *args, tag=None, metadata=None, message_stream=None, **kwargs):
        self.tag = tag
        self.metadata = metadata
        self.message_stream = message_stream
        super().__init__(*args, **kwargs)


class PostmarkEmailMessage(PostmarkEmailMixin, EmailMessage):
    pass


class PostmarkEmailMultiAlternatives(PostmarkEmailMixin, EmailMultiAlternatives):
    pass
