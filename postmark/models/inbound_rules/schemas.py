from typing import List

from pydantic import BaseModel, ConfigDict, Field


class InboundRule(BaseModel):
    """A single inbound rule trigger returned by create and list endpoints."""

    id: int = Field(alias="ID")
    rule: str = Field(alias="Rule")

    model_config = ConfigDict(populate_by_name=True)


class InboundRulesListResponse(BaseModel):
    """Response from ``GET /triggers/inboundrules``."""

    total_count: int = Field(alias="TotalCount")
    inbound_rules: List[InboundRule] = Field(alias="InboundRules")

    model_config = ConfigDict(populate_by_name=True)


class DeleteInboundRuleResponse(BaseModel):
    """Response from ``DELETE /triggers/inboundrules/{triggerid}``."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)
