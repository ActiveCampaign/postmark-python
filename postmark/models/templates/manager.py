import logging
from typing import Any

from pydantic import ValidationError

from postmark.exceptions import InvalidEmailException
from postmark.models.page import Page
from postmark.utils.types import HTTPClient

from .enums import TemplateTypeFilter
from .schemas import (
    CreateTemplateRequest,
    DeleteTemplateResponse,
    EditTemplateRequest,
    Template,
    TemplateListResponse,
    TemplateSummary,
    UpsertTemplateResponse,
    ValidateTemplateRequest,
    ValidateTemplateResponse,
)

logger = logging.getLogger(__name__)


def _parse_request(model_cls, data):
    if isinstance(data, model_cls):
        return data
    try:
        return model_cls.model_validate(data)
    except ValidationError as e:
        raise InvalidEmailException(e.errors()) from e


class TemplateManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def get(self, template_id_or_alias: int | str) -> Template:
        """Get a template by ID or alias."""
        response = await self.client.get(f"/templates/{template_id_or_alias}")
        return Template(**response.json())

    async def create(
        self, request: CreateTemplateRequest | dict[str, Any]
    ) -> UpsertTemplateResponse:
        """Create a new template."""
        req = _parse_request(CreateTemplateRequest, request)
        response = await self.client.post(
            "/templates",
            json=req.model_dump(by_alias=True, exclude_none=True),
        )
        return UpsertTemplateResponse(**response.json())

    async def edit(
        self,
        template_id_or_alias: int | str,
        request: EditTemplateRequest | dict[str, Any],
    ) -> UpsertTemplateResponse:
        """Edit an existing template."""
        req = _parse_request(EditTemplateRequest, request)
        response = await self.client.put(
            f"/templates/{template_id_or_alias}",
            json=req.model_dump(by_alias=True, exclude_none=True),
        )
        return UpsertTemplateResponse(**response.json())

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
        template_type: TemplateTypeFilter | None = None,
    ) -> Page[TemplateSummary]:
        """List templates with optional type filter."""
        if count > 500:
            raise ValueError("count cannot exceed 500 templates per request")
        if count + offset > 10000:
            raise ValueError("count + offset cannot exceed 10,000 templates")

        params: dict[str, Any] = {"count": count, "offset": offset}
        if template_type is not None:
            params["templateType"] = template_type.value

        response = await self.client.get("/templates", params=params)
        data = TemplateListResponse(**response.json())
        return Page(items=data.templates, total=data.total_count)

    async def delete(self, template_id_or_alias: int | str) -> DeleteTemplateResponse:
        """Delete a template by ID or alias."""
        response = await self.client.delete(f"/templates/{template_id_or_alias}")
        return DeleteTemplateResponse(**response.json())

    async def validate(
        self, request: ValidateTemplateRequest | dict[str, Any]
    ) -> ValidateTemplateResponse:
        """Validate template content."""
        req = _parse_request(ValidateTemplateRequest, request)
        response = await self.client.post(
            "/templates/validate",
            json=req.model_dump(by_alias=True, exclude_none=True),
        )
        return ValidateTemplateResponse(**response.json())
