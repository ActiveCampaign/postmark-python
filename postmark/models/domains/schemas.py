from pydantic import BaseModel, ConfigDict, Field


class DomainListItem(BaseModel):
    """Minimal domain info returned by ``GET /domains``."""

    id: int = Field(alias="ID")
    name: str = Field(alias="Name")
    spf_verified: bool = Field(alias="SPFVerified")  # deprecated by Postmark
    dkim_verified: bool = Field(alias="DKIMVerified")
    weak_dkim: bool = Field(alias="WeakDKIM")
    return_path_domain_verified: bool = Field(alias="ReturnPathDomainVerified")

    model_config = ConfigDict(populate_by_name=True)


class Domain(BaseModel):
    """Full domain details returned by create, get, edit, and verification endpoints."""

    id: int = Field(alias="ID")
    name: str = Field(alias="Name")
    spf_verified: bool = Field(False, alias="SPFVerified")  # deprecated by Postmark
    spf_host: str | None = Field(None, alias="SPFHost")
    spf_text_value: str | None = Field(None, alias="SPFTextValue")
    dkim_verified: bool = Field(alias="DKIMVerified")
    weak_dkim: bool = Field(alias="WeakDKIM")
    dkim_host: str | None = Field(None, alias="DKIMHost")
    dkim_text_value: str | None = Field(None, alias="DKIMTextValue")
    dkim_pending_host: str | None = Field(None, alias="DKIMPendingHost")
    dkim_pending_text_value: str | None = Field(None, alias="DKIMPendingTextValue")
    dkim_revoked_host: str | None = Field(None, alias="DKIMRevokedHost")
    dkim_revoked_text_value: str | None = Field(None, alias="DKIMRevokedTextValue")
    safe_to_remove_revoked_key_from_dns: bool | None = Field(
        None, alias="SafeToRemoveRevokedKeyFromDNS"
    )
    dkim_update_status: str | None = Field(None, alias="DKIMUpdateStatus")
    return_path_domain: str | None = Field(None, alias="ReturnPathDomain")
    return_path_domain_verified: bool | None = Field(
        None, alias="ReturnPathDomainVerified"
    )
    return_path_domain_cname_value: str | None = Field(
        None, alias="ReturnPathDomainCNAMEValue"
    )

    model_config = ConfigDict(populate_by_name=True)


class DomainsListResponse(BaseModel):
    """Response from ``GET /domains``."""

    total_count: int = Field(alias="TotalCount")
    domains: list[DomainListItem] = Field(alias="Domains")

    model_config = ConfigDict(populate_by_name=True)


class DeleteDomainResponse(BaseModel):
    """Response from ``DELETE /domains/{domainid}``."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class SPFVerificationResponse(BaseModel):
    """Response from ``POST /domains/{domainid}/verifyspf`` (deprecated by Postmark)."""

    spf_host: str = Field(alias="SPFHost")
    spf_verified: bool = Field(alias="SPFVerified")
    spf_text_value: str = Field(alias="SPFTextValue")

    model_config = ConfigDict(populate_by_name=True)
