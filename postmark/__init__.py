import logging
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("postmark")
except PackageNotFoundError:  # running from source without install
    __version__ = "0.0.0"

from .clients.account_client import AccountClient
from .clients.server_client import ServerClient
from .exceptions import (
    InactiveRecipientException,
    InvalidAPIKeyException,
    InvalidEmailException,
    PostmarkAPIException,
    PostmarkException,
    RateLimitException,
    ServerException,
    TimeoutException,
    ValidationException,
)
from .models import outbound
from .models.outbound import Attachment, Email, Header, Message, SendResponse
from .models.page import Page
from .utils import server_utils

# Base logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = [
    "ServerClient",
    "AccountClient",
    "Email",
    "Message",
    "SendResponse",
    "Attachment",
    "Header",
    "outbound",
    "PostmarkException",
    "PostmarkAPIException",
    "InvalidAPIKeyException",
    "InvalidEmailException",
    "InactiveRecipientException",
    "ValidationException",
    "RateLimitException",
    "ServerException",
    "TimeoutException",
    "server_utils",
    "Page",
    "__version__",
]
