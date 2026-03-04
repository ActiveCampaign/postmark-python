from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SenderSignatureListItem(BaseModel):
    """Minimal sender signature info returned by ``GET /senders``."""

    id: int = Field(alias="ID")
    domain: str = Field(alias="Domain")
    email_address: str = Field(alias="EmailAddress")
    reply_to_email_address: str = Field(alias="ReplyToEmailAddress")
    name: str = Field(alias="Name")
    confirmed: bool = Field(alias="Confirmed")

    model_config = ConfigDict(populate_by_name=True)


class SenderSignature(BaseModel):
    """Full sender signature details returned by create, get, edit, and verification endpoints."""

    id: int = Field(alias="ID")
    domain: str = Field(alias="Domain")
    email_address: str = Field(alias="EmailAddress")
    reply_to_email_address: str = Field(alias="ReplyToEmailAddress")
    name: str = Field(alias="Name")
    confirmed: bool = Field(alias="Confirmed")
    spf_verified: bool = Field(False, alias="SPFVerified")  # deprecated by Postmark
    spf_host: Optional[str] = Field(None, alias="SPFHost")
    spf_text_value: Optional[str] = Field(None, alias="SPFTextValue")
    dkim_verified: bool = Field(alias="DKIMVerified")
    weak_dkim: bool = Field(alias="WeakDKIM")
    dkim_host: Optional[str] = Field(None, alias="DKIMHost")
    dkim_text_value: Optional[str] = Field(None, alias="DKIMTextValue")
    dkim_pending_host: Optional[str] = Field(None, alias="DKIMPendingHost")
    dkim_pending_text_value: Optional[str] = Field(None, alias="DKIMPendingTextValue")
    dkim_revoked_host: Optional[str] = Field(None, alias="DKIMRevokedHost")
    dkim_revoked_text_value: Optional[str] = Field(None, alias="DKIMRevokedTextValue")
    safe_to_remove_revoked_key_from_dns: Optional[bool] = Field(
        None, alias="SafeToRemoveRevokedKeyFromDNS"
    )
    dkim_update_status: Optional[str] = Field(None, alias="DKIMUpdateStatus")
    return_path_domain: Optional[str] = Field(None, alias="ReturnPathDomain")
    return_path_domain_verified: Optional[bool] = Field(
        None, alias="ReturnPathDomainVerified"
    )
    return_path_domain_cname_value: Optional[str] = Field(
        None, alias="ReturnPathDomainCNAMEValue"
    )
    confirmation_personal_note: Optional[str] = Field(
        None, alias="ConfirmationPersonalNote"
    )

    model_config = ConfigDict(populate_by_name=True)


class SenderSignaturesListResponse(BaseModel):
    """Response from ``GET /senders``."""

    total_count: int = Field(alias="TotalCount")
    sender_signatures: List[SenderSignatureListItem] = Field(alias="SenderSignatures")

    model_config = ConfigDict(populate_by_name=True)


class DeleteSignatureResponse(BaseModel):
    """Response from ``DELETE /senders/{signatureid}``."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class ResendConfirmationResponse(BaseModel):
    """Response from ``POST /senders/{signatureid}/resend``."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class RequestNewDKIMResponse(BaseModel):
    """Response from ``POST /senders/{signatureid}/requestnewdkim`` (deprecated by Postmark)."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)
