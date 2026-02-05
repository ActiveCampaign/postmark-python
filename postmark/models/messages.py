import logging
import re
from datetime import datetime


from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Optional,
    Union,
    TYPE_CHECKING,
    AsyncGenerator,
)

from ..utils.message_utils import validate_formatted_email, validate_email_list

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    TypeAdapter,
    ValidationError,
)

if TYPE_CHECKING:
    # Prevent circular import at runtime
    from .server_client import ServerClient

email_adapter = TypeAdapter(EmailStr)

logger = logging.getLogger(__name__)

FormattedEmailStr = Annotated[str, BeforeValidator(validate_formatted_email)]
EmailList = Annotated[List[str], BeforeValidator(validate_email_list)]
