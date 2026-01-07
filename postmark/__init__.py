import logging

# Base Logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Export exceptions for easy access
from .exceptions import (InactiveRecipientException, InvalidAPIKeyException,
                         PostmarkAPIException, PostmarkException,
                         RateLimitException, ServerException, TimeoutException,
                         ValidationException)
# Import modules
from .models import client, messages

__all__ = [
    "client",
    "messages",
    "PostmarkException",
    "PostmarkAPIException",
    "InvalidAPIKeyException",
    "InactiveRecipientException",
    "ValidationException",
    "RateLimitException",
    "ServerException",
    "TimeoutException",
]
