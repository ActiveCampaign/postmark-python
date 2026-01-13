import logging

# Base Logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Export exceptions for easy access
from .exceptions import (
    InactiveRecipientException,
    InvalidAPIKeyException,
    PostmarkAPIException,
    PostmarkException,
    RateLimitException,
    ServerException,
    TimeoutException,
    ValidationException,
)

# Import modules
from .clients.server_client import ServerClient
from .models import messages
from .utils import server_utils

__all__ = [
    "ServerClient",
    "messages",
    "PostmarkException",
    "PostmarkAPIException",
    "InvalidAPIKeyException",
    "InactiveRecipientException",
    "ValidationException",
    "RateLimitException",
    "ServerException",
    "TimeoutException",
    "server_utils",
]
