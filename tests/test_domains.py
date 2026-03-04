"""Tests for DomainManager."""

import pytest

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

DOMAIN_LIST_ITEM = {
    "ID": 10,
    "Name": "example.com",
    "SPFVerified": False,
    "DKIMVerified": True,
    "WeakDKIM": False,
    "ReturnPathDomainVerified": True,
}

DOMAIN = {
    "ID": 10,
    "Name": "example.com",
    "SPFVerified": False,
    "SPFHost": "example.com",
    "SPFTextValue": "v=spf1 a mx ~all",
    "DKIMVerified": True,
    "WeakDKIM": False,
    "DKIMHost": "20240101._domainkey.example.com",
    "DKIMTextValue": "v=DKIM1; k=rsa; p=ABC123",
    "DKIMPendingHost": "",
    "DKIMPendingTextValue": "",
    "DKIMRevokedHost": "",
    "DKIMRevokedTextValue": "",
    "SafeToRemoveRevokedKeyFromDNS": False,
    "DKIMUpdateStatus": "Verified",
    "ReturnPathDomain": "pm-bounces.example.com",
    "ReturnPathDomainVerified": True,
    "ReturnPathDomainCNAMEValue": "pm.mtasv.net",
}

ROTATE_DKIM_RESPONSE = {
    "ID": 10,
    "Name": "example.com",
    "DKIMVerified": True,
    "WeakDKIM": False,
    "DKIMHost": "20240101._domainkey.example.com",
    "DKIMTextValue": "v=DKIM1; k=rsa; p=ABC123",
    "DKIMPendingHost": "20250101._domainkey.example.com",
    "DKIMPendingTextValue": "v=DKIM1; k=rsa; p=XYZ789",
    "DKIMRevokedHost": "",
    "DKIMRevokedTextValue": "",
    "SafeToRemoveRevokedKeyFromDNS": False,
    "DKIMUpdateStatus": "Pending",
}

DELETE_RESPONSE = {"ErrorCode": 0, "Message": "Domain removed."}

SPF_RESPONSE = {
    "SPFHost": "example.com",
    "SPFVerified": True,
    "SPFTextValue": "v=spf1 include:spf.mtasv.net ~all",
}


def _make_domain(**overrides) -> dict:
    return {**DOMAIN, **overrides}


# ---------------------------------------------------------------------------
# List domains
# ---------------------------------------------------------------------------


class TestListDomains:
    @pytest.fixture
    def list_response(self):
        return {
            "TotalCount": 2,
            "Domains": [
                {**DOMAIN_LIST_ITEM, "ID": 1, "Name": "alpha.com"},
                {**DOMAIN_LIST_ITEM, "ID": 2, "Name": "beta.com"},
            ],
        }

    @pytest.mark.asyncio
    async def test_list_success(self, domains, list_response):
        manager, fake = domains
        fake.mock_get_response(list_response)

        result = await manager.list()

        assert result.total == 2
        assert len(result.items) == 2
        assert result.items[0].name == "alpha.com"
        assert result.items[1].name == "beta.com"

    @pytest.mark.asyncio
    async def test_list_default_params(self, domains):
        manager, fake = domains
        fake.mock_get_response({"TotalCount": 0, "Domains": []})

        await manager.list()

        fake.get.assert_called_once_with("/domains", params={"count": 100, "offset": 0})

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, domains):
        manager, fake = domains
        fake.mock_get_response({"TotalCount": 0, "Domains": []})

        await manager.list(count=50, offset=100)

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 50
        assert params["offset"] == 100

    @pytest.mark.asyncio
    async def test_list_empty(self, domains):
        manager, fake = domains
        fake.mock_get_response({"TotalCount": 0, "Domains": []})

        result = await manager.list()

        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_list_item_fields(self, domains):
        manager, fake = domains
        fake.mock_get_response({"TotalCount": 1, "Domains": [DOMAIN_LIST_ITEM]})

        result = await manager.list()

        item = result.items[0]
        assert item.id == 10
        assert item.name == "example.com"
        assert item.dkim_verified is True
        assert item.weak_dkim is False
        assert item.return_path_domain_verified is True


# ---------------------------------------------------------------------------
# Get domain
# ---------------------------------------------------------------------------


class TestGetDomain:
    @pytest.mark.asyncio
    async def test_get_success(self, domains):
        manager, fake = domains
        fake.mock_get_response(DOMAIN)

        domain = await manager.get(10)

        assert domain.id == 10
        assert domain.name == "example.com"
        assert domain.dkim_verified is True
        assert domain.return_path_domain == "pm-bounces.example.com"

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, domains):
        manager, fake = domains
        fake.mock_get_response(DOMAIN)

        await manager.get(10)

        fake.get.assert_called_once_with("/domains/10")

    @pytest.mark.asyncio
    async def test_get_different_domain_id(self, domains):
        manager, fake = domains
        fake.mock_get_response(_make_domain(ID=999))

        await manager.get(999)

        fake.get.assert_called_once_with("/domains/999")


# ---------------------------------------------------------------------------
# Create domain
# ---------------------------------------------------------------------------


class TestCreateDomain:
    @pytest.mark.asyncio
    async def test_create_name_only(self, domains):
        manager, fake = domains
        fake.mock_post_response(DOMAIN)

        domain = await manager.create(name="example.com")

        assert domain.name == "example.com"
        fake.post.assert_called_once_with("/domains", json={"Name": "example.com"})

    @pytest.mark.asyncio
    async def test_create_with_return_path_domain(self, domains):
        manager, fake = domains
        fake.mock_post_response(DOMAIN)

        await manager.create(
            name="example.com", return_path_domain="pm-bounces.example.com"
        )

        body = fake.post.call_args[1]["json"]
        assert body["Name"] == "example.com"
        assert body["ReturnPathDomain"] == "pm-bounces.example.com"

    @pytest.mark.asyncio
    async def test_create_omits_none_return_path(self, domains):
        manager, fake = domains
        fake.mock_post_response(DOMAIN)

        await manager.create(name="example.com")

        body = fake.post.call_args[1]["json"]
        assert "ReturnPathDomain" not in body


# ---------------------------------------------------------------------------
# Edit domain
# ---------------------------------------------------------------------------


class TestEditDomain:
    @pytest.mark.asyncio
    async def test_edit_return_path_domain(self, domains):
        manager, fake = domains
        fake.mock_put_response(DOMAIN)

        domain = await manager.edit(10, return_path_domain="pm-bounces.example.com")

        assert domain.id == 10
        fake.put.assert_called_once_with(
            "/domains/10", json={"ReturnPathDomain": "pm-bounces.example.com"}
        )

    @pytest.mark.asyncio
    async def test_edit_no_args_sends_empty_body(self, domains):
        manager, fake = domains
        fake.mock_put_response(DOMAIN)

        await manager.edit(10)

        fake.put.assert_called_once_with("/domains/10", json={})

    @pytest.mark.asyncio
    async def test_edit_calls_correct_endpoint(self, domains):
        manager, fake = domains
        fake.mock_put_response(DOMAIN)

        await manager.edit(99, return_path_domain="bounces.example.com")

        fake.put.assert_called_once_with(
            "/domains/99", json={"ReturnPathDomain": "bounces.example.com"}
        )


# ---------------------------------------------------------------------------
# Delete domain
# ---------------------------------------------------------------------------


class TestDeleteDomain:
    @pytest.mark.asyncio
    async def test_delete_success(self, domains):
        manager, fake = domains
        fake.mock_delete_response(DELETE_RESPONSE)

        result = await manager.delete(10)

        assert result.error_code == 0
        assert result.message == "Domain removed."

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self, domains):
        manager, fake = domains
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(10)

        fake.delete.assert_called_once_with("/domains/10")

    @pytest.mark.asyncio
    async def test_delete_does_not_call_other_methods(self, domains):
        manager, fake = domains
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(10)

        fake.get.assert_not_called()
        fake.post.assert_not_called()
        fake.put.assert_not_called()


# ---------------------------------------------------------------------------
# Verify DKIM
# ---------------------------------------------------------------------------


class TestVerifyDkim:
    @pytest.mark.asyncio
    async def test_verify_dkim_success(self, domains):
        manager, fake = domains
        fake.mock_put_response(_make_domain(DKIMVerified=True))

        domain = await manager.verify_dkim(10)

        assert domain.dkim_verified is True

    @pytest.mark.asyncio
    async def test_verify_dkim_calls_correct_endpoint(self, domains):
        manager, fake = domains
        fake.mock_put_response(DOMAIN)

        await manager.verify_dkim(10)

        fake.put.assert_called_once_with("/domains/10/verifyDkim")

    @pytest.mark.asyncio
    async def test_verify_dkim_sends_no_body(self, domains):
        manager, fake = domains
        fake.mock_put_response(DOMAIN)

        await manager.verify_dkim(10)

        # put called with no json body
        args, kwargs = fake.put.call_args
        assert kwargs.get("json") is None


# ---------------------------------------------------------------------------
# Verify Return-Path
# ---------------------------------------------------------------------------


class TestVerifyReturnPath:
    @pytest.mark.asyncio
    async def test_verify_return_path_success(self, domains):
        manager, fake = domains
        fake.mock_put_response(_make_domain(ReturnPathDomainVerified=True))

        domain = await manager.verify_return_path(10)

        assert domain.return_path_domain_verified is True

    @pytest.mark.asyncio
    async def test_verify_return_path_calls_correct_endpoint(self, domains):
        manager, fake = domains
        fake.mock_put_response(DOMAIN)

        await manager.verify_return_path(10)

        fake.put.assert_called_once_with("/domains/10/verifyReturnPath")

    @pytest.mark.asyncio
    async def test_verify_return_path_sends_no_body(self, domains):
        manager, fake = domains
        fake.mock_put_response(DOMAIN)

        await manager.verify_return_path(10)

        args, kwargs = fake.put.call_args
        assert kwargs.get("json") is None


# ---------------------------------------------------------------------------
# Verify SPF (deprecated)
# ---------------------------------------------------------------------------


class TestVerifySpf:
    @pytest.mark.asyncio
    async def test_verify_spf_success(self, domains):
        manager, fake = domains
        fake.mock_post_response(SPF_RESPONSE)

        result = await manager.verify_spf(10)

        assert result.spf_verified is True
        assert result.spf_host == "example.com"
        assert result.spf_text_value == "v=spf1 include:spf.mtasv.net ~all"

    @pytest.mark.asyncio
    async def test_verify_spf_calls_correct_endpoint(self, domains):
        manager, fake = domains
        fake.mock_post_response(SPF_RESPONSE)

        await manager.verify_spf(10)

        fake.post.assert_called_once_with("/domains/10/verifyspf")


# ---------------------------------------------------------------------------
# Rotate DKIM
# ---------------------------------------------------------------------------


class TestRotateDkim:
    @pytest.mark.asyncio
    async def test_rotate_dkim_success(self, domains):
        manager, fake = domains
        fake.mock_post_response(ROTATE_DKIM_RESPONSE)

        domain = await manager.rotate_dkim(10)

        assert domain.id == 10
        assert domain.dkim_update_status == "Pending"
        assert domain.dkim_pending_host == "20250101._domainkey.example.com"

    @pytest.mark.asyncio
    async def test_rotate_dkim_calls_correct_endpoint(self, domains):
        manager, fake = domains
        fake.mock_post_response(ROTATE_DKIM_RESPONSE)

        await manager.rotate_dkim(10)

        fake.post.assert_called_once_with("/domains/10/rotatedkim")

    @pytest.mark.asyncio
    async def test_rotate_dkim_sends_no_body(self, domains):
        manager, fake = domains
        fake.mock_post_response(ROTATE_DKIM_RESPONSE)

        await manager.rotate_dkim(10)

        args, kwargs = fake.post.call_args
        assert kwargs.get("json") is None
