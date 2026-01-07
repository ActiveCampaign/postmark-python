import logging

# Base Logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Import modules
from .models import client
from .models import messages

# Export exceptions for easy access
from .exceptions import (
    PostmarkException,
    PostmarkAPIException,
    InvalidAPIKeyException,
    InactiveRecipientException,
    ValidationException,
    RateLimitException,
    ServerException,
    TimeoutException,
)

__all__ = [
    'client',
    'messages',
    'PostmarkException',
    'PostmarkAPIException',
    'InvalidAPIKeyException',
    'InactiveRecipientException',
    'ValidationException',
    'RateLimitException',
    'ServerException',
    'TimeoutException',
]