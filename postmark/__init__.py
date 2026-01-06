import logging
from .models import client
from .models import messages

# Base logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

