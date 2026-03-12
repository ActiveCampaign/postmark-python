"""Tests for SenderSignatureManager."""

import pytest

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

SIGNATURE_LIST_ITEM = {
    "ID": 20,
    "Domain": "example.com",
    "EmailAddress": "sender@example.com",
    "ReplyToEmailAddress": "",
    "Name": "Sender Name",
    "Confirmed": True,
}

SIGNATURE = {
    "ID": 20,
    "Domain": "example.com",
    "EmailAddress": "sender@example.com",
    "ReplyToEmailAddress": "",
    "Name": "Sender Name",
    "Confirmed": True,
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
    "ConfirmationPersonalNote": None,
}

DELETE_RESPONSE = {"ErrorCode": 0, "Message": "Signature removed."}
RESEND_RESPONSE = {"ErrorCode": 0, "Message": "Confirmation email has been re-sent."}
NEW_DKIM_RESPONSE = {"ErrorCode": 0, "Message": "New DKIM has been requested."}


def _make_signature(**overrides) -> dict:
    return {**SIGNATURE, **overrides}


# ---------------------------------------------------------------------------
# List signatures
# ---------------------------------------------------------------------------


class TestListSignatures:
    @pytest.fixture
    def list_response(self):
        return {
            "TotalCount": 2,
            "SenderSignatures": [
                {**SIGNATURE_LIST_ITEM, "ID": 1, "EmailAddress": "a@example.com"},
                {**SIGNATURE_LIST_ITEM, "ID": 2, "EmailAddress": "b@example.com"},
            ],
        }

    @pytest.mark.asyncio
    async def test_list_success(self, signatures, list_response):
        manager, fake = signatures
        fake.mock_get_response(list_response)

        result = await manager.list()

        assert result.total == 2
        assert len(result.items) == 2
        assert result.items[0].email_address == "a@example.com"
        assert result.items[1].email_address == "b@example.com"

    @pytest.mark.asyncio
    async def test_list_default_params(self, signatures):
        manager, fake = signatures
        fake.mock_get_response({"TotalCount": 0, "SenderSignatures": []})

        await manager.list()

        fake.get.assert_called_once_with("/senders", params={"count": 100, "offset": 0})

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, signatures):
        manager, fake = signatures
        fake.mock_get_response({"TotalCount": 0, "SenderSignatures": []})

        await manager.list(count=25, offset=50)

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 25
        assert params["offset"] == 50

    @pytest.mark.asyncio
    async def test_list_empty(self, signatures):
        manager, fake = signatures
        fake.mock_get_response({"TotalCount": 0, "SenderSignatures": []})

        result = await manager.list()

        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_list_item_fields(self, signatures):
        manager, fake = signatures
        fake.mock_get_response(
            {"TotalCount": 1, "SenderSignatures": [SIGNATURE_LIST_ITEM]}
        )

        result = await manager.list()

        item = result.items[0]
        assert item.id == 20
        assert item.domain == "example.com"
        assert item.email_address == "sender@example.com"
        assert item.name == "Sender Name"
        assert item.confirmed is True


# ---------------------------------------------------------------------------
# Get signature
# ---------------------------------------------------------------------------


class TestGetSignature:
    @pytest.mark.asyncio
    async def test_get_success(self, signatures):
        manager, fake = signatures
        fake.mock_get_response(SIGNATURE)

        sig = await manager.get(20)

        assert sig.id == 20
        assert sig.email_address == "sender@example.com"
        assert sig.dkim_verified is True
        assert sig.return_path_domain == "pm-bounces.example.com"

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, signatures):
        manager, fake = signatures
        fake.mock_get_response(SIGNATURE)

        await manager.get(20)

        fake.get.assert_called_once_with("/senders/20")

    @pytest.mark.asyncio
    async def test_get_different_signature_id(self, signatures):
        manager, fake = signatures
        fake.mock_get_response(_make_signature(ID=999))

        await manager.get(999)

        fake.get.assert_called_once_with("/senders/999")


# ---------------------------------------------------------------------------
# Create signature
# ---------------------------------------------------------------------------


class TestCreateSignature:
    @pytest.mark.asyncio
    async def test_create_required_fields_only(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(SIGNATURE)

        sig = await manager.create(sender="sender@example.com", name="Sender Name")

        assert sig.email_address == "sender@example.com"
        fake.post.assert_called_once_with(
            "/senders",
            json={"FromEmail": "sender@example.com", "Name": "Sender Name"},
        )

    @pytest.mark.asyncio
    async def test_create_with_reply_to_email(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(SIGNATURE)

        await manager.create(
            sender="sender@example.com",
            name="Sender Name",
            reply_to="reply@example.com",
        )

        body = fake.post.call_args[1]["json"]
        assert body["ReplyToEmail"] == "reply@example.com"

    @pytest.mark.asyncio
    async def test_create_with_return_path_domain(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(SIGNATURE)

        await manager.create(
            sender="sender@example.com",
            name="Sender Name",
            return_path_domain="pm-bounces.example.com",
        )

        body = fake.post.call_args[1]["json"]
        assert body["ReturnPathDomain"] == "pm-bounces.example.com"

    @pytest.mark.asyncio
    async def test_create_with_confirmation_note(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(SIGNATURE)

        await manager.create(
            sender="sender@example.com",
            name="Sender Name",
            confirmation_personal_note="Please confirm your email.",
        )

        body = fake.post.call_args[1]["json"]
        assert body["ConfirmationPersonalNote"] == "Please confirm your email."

    @pytest.mark.asyncio
    async def test_create_omits_none_optional_fields(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(SIGNATURE)

        await manager.create(sender="sender@example.com", name="Sender Name")

        body = fake.post.call_args[1]["json"]
        assert "ReplyToEmail" not in body
        assert "ReturnPathDomain" not in body
        assert "ConfirmationPersonalNote" not in body

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(SIGNATURE)

        await manager.create(
            sender="sender@example.com",
            name="Sender Name",
            reply_to="reply@example.com",
            return_path_domain="pm-bounces.example.com",
            confirmation_personal_note="Hello!",
        )

        body = fake.post.call_args[1]["json"]
        assert body["FromEmail"] == "sender@example.com"
        assert body["Name"] == "Sender Name"
        assert body["ReplyToEmail"] == "reply@example.com"
        assert body["ReturnPathDomain"] == "pm-bounces.example.com"
        assert body["ConfirmationPersonalNote"] == "Hello!"


# ---------------------------------------------------------------------------
# Edit signature
# ---------------------------------------------------------------------------


class TestEditSignature:
    @pytest.mark.asyncio
    async def test_edit_name_only(self, signatures):
        manager, fake = signatures
        fake.mock_put_response(_make_signature(Name="Updated Name"))

        sig = await manager.edit(20, name="Updated Name")

        assert sig.name == "Updated Name"
        fake.put.assert_called_once_with("/senders/20", json={"Name": "Updated Name"})

    @pytest.mark.asyncio
    async def test_edit_calls_correct_endpoint(self, signatures):
        manager, fake = signatures
        fake.mock_put_response(SIGNATURE)

        await manager.edit(99, name="X")

        fake.put.assert_called_once_with("/senders/99", json={"Name": "X"})

    @pytest.mark.asyncio
    async def test_edit_with_reply_to(self, signatures):
        manager, fake = signatures
        fake.mock_put_response(SIGNATURE)

        await manager.edit(20, name="Sender", reply_to="reply@example.com")

        body = fake.put.call_args[1]["json"]
        assert body["ReplyToEmail"] == "reply@example.com"

    @pytest.mark.asyncio
    async def test_edit_with_return_path_domain(self, signatures):
        manager, fake = signatures
        fake.mock_put_response(SIGNATURE)

        await manager.edit(
            20, name="Sender", return_path_domain="pm-bounces.example.com"
        )

        body = fake.put.call_args[1]["json"]
        assert body["ReturnPathDomain"] == "pm-bounces.example.com"

    @pytest.mark.asyncio
    async def test_edit_with_confirmation_note(self, signatures):
        manager, fake = signatures
        fake.mock_put_response(SIGNATURE)

        await manager.edit(20, name="Sender", confirmation_personal_note="Note.")

        body = fake.put.call_args[1]["json"]
        assert body["ConfirmationPersonalNote"] == "Note."

    @pytest.mark.asyncio
    async def test_edit_omits_none_optional_fields(self, signatures):
        manager, fake = signatures
        fake.mock_put_response(SIGNATURE)

        await manager.edit(20, name="Sender")

        body = fake.put.call_args[1]["json"]
        assert body == {"Name": "Sender"}


# ---------------------------------------------------------------------------
# Delete signature
# ---------------------------------------------------------------------------


class TestDeleteSignature:
    @pytest.mark.asyncio
    async def test_delete_success(self, signatures):
        manager, fake = signatures
        fake.mock_delete_response(DELETE_RESPONSE)

        result = await manager.delete(20)

        assert result.error_code == 0
        assert result.message == "Signature removed."

    @pytest.mark.asyncio
    async def test_delete_calls_correct_endpoint(self, signatures):
        manager, fake = signatures
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(20)

        fake.delete.assert_called_once_with("/senders/20")

    @pytest.mark.asyncio
    async def test_delete_does_not_call_other_methods(self, signatures):
        manager, fake = signatures
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete(20)

        fake.get.assert_not_called()
        fake.post.assert_not_called()
        fake.put.assert_not_called()


# ---------------------------------------------------------------------------
# Resend confirmation
# ---------------------------------------------------------------------------


class TestResendConfirmation:
    @pytest.mark.asyncio
    async def test_resend_success(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(RESEND_RESPONSE)

        result = await manager.resend_confirmation(20)

        assert result.error_code == 0
        assert result.message == "Confirmation email has been re-sent."

    @pytest.mark.asyncio
    async def test_resend_calls_correct_endpoint(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(RESEND_RESPONSE)

        await manager.resend_confirmation(20)

        fake.post.assert_called_once_with("/senders/20/resend")

    @pytest.mark.asyncio
    async def test_resend_sends_no_body(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(RESEND_RESPONSE)

        await manager.resend_confirmation(20)

        args, kwargs = fake.post.call_args
        assert kwargs.get("json") is None


# ---------------------------------------------------------------------------
# Verify SPF (deprecated)
# ---------------------------------------------------------------------------


class TestVerifySpf:
    @pytest.mark.asyncio
    async def test_verify_spf_success(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(_make_signature(SPFVerified=True))

        sig = await manager.verify_spf(20)

        assert sig.spf_verified is True

    @pytest.mark.asyncio
    async def test_verify_spf_calls_correct_endpoint(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(SIGNATURE)

        await manager.verify_spf(20)

        fake.post.assert_called_once_with("/senders/20/verifyspf")


# ---------------------------------------------------------------------------
# Request new DKIM (deprecated)
# ---------------------------------------------------------------------------


class TestRequestNewDkim:
    @pytest.mark.asyncio
    async def test_request_new_dkim_success(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(NEW_DKIM_RESPONSE)

        result = await manager.request_new_dkim(20)

        assert result.error_code == 0
        assert result.message == "New DKIM has been requested."

    @pytest.mark.asyncio
    async def test_request_new_dkim_calls_correct_endpoint(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(NEW_DKIM_RESPONSE)

        await manager.request_new_dkim(20)

        fake.post.assert_called_once_with("/senders/20/requestnewdkim")

    @pytest.mark.asyncio
    async def test_request_new_dkim_sends_no_body(self, signatures):
        manager, fake = signatures
        fake.mock_post_response(NEW_DKIM_RESPONSE)

        await manager.request_new_dkim(20)

        args, kwargs = fake.post.call_args
        assert kwargs.get("json") is None
