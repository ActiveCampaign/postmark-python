from typing import Any, Dict, Union

from pydantic import ValidationError

from postmark.exceptions import InvalidEmailException
from postmark.utils.types import HTTPClient


class AccountTemplateManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def push(self, request: Union[Dict[str, Any], Any]) -> Any:
        """Push templates from one server to another."""
        from .schemas import PushTemplatesRequest, PushTemplatesResponse

        if not isinstance(request, PushTemplatesRequest):
            try:
                request = PushTemplatesRequest.model_validate(request)
            except ValidationError as e:
                raise InvalidEmailException(e.errors()) from e

        response = await self.client.put(
            "/templates/push",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return PushTemplatesResponse(**response.json())
