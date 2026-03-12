"""Tests for the TemplateManager."""

import pytest

from postmark.models.templates import (
    CreateTemplateRequest,
    EditTemplateRequest,
    PushTemplatesRequest,
    TemplateType,
    TemplateTypeFilter,
    ValidateTemplateRequest,
)

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

TEMPLATE_SUMMARY = {
    "Active": True,
    "TemplateId": 1,
    "Name": "Welcome",
    "Alias": "welcome",
    "TemplateType": "Standard",
    "LayoutTemplate": None,
}

TEMPLATE = {
    "TemplateId": 1,
    "Name": "Welcome",
    "Subject": "Hello {{name}}",
    "HtmlBody": "<p>Hello {{name}}</p>",
    "TextBody": "Hello {{name}}",
    "AssociatedServerId": 42,
    "Active": True,
    "Alias": "welcome",
    "TemplateType": "Standard",
    "LayoutTemplate": None,
}

UPSERT_RESPONSE = {
    "TemplateId": 1,
    "Name": "Welcome",
    "Active": True,
    "Alias": "welcome",
    "TemplateType": "Standard",
    "LayoutTemplate": None,
}

DELETE_RESPONSE = {
    "ErrorCode": 0,
    "Message": "Template removed.",
}

VALIDATE_RESPONSE = {
    "AllContentIsValid": True,
    "HtmlBody": {
        "ContentIsValid": True,
        "ValidationErrors": [],
        "RenderedContent": "<p>Hello World</p>",
    },
    "TextBody": {
        "ContentIsValid": True,
        "ValidationErrors": [],
        "RenderedContent": "Hello World",
    },
    "Subject": {
        "ContentIsValid": True,
        "ValidationErrors": [],
        "RenderedContent": "Hello World",
    },
    "SuggestedTemplateModel": {"name": "World"},
}

PUSH_RESPONSE = {
    "TotalCount": 1,
    "Templates": [
        {
            "Action": "Create",
            "TemplateId": 1,
            "Alias": "welcome",
            "Name": "Welcome",
            "TemplateType": "Standard",
        }
    ],
}


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


class TestGetTemplate:
    @pytest.mark.asyncio
    async def test_get_by_id(self, templates):
        manager, fake = templates
        fake.mock_get_response(TEMPLATE)

        result = await manager.get(1)

        assert result.template_id == 1
        assert result.name == "Welcome"
        fake.get.assert_called_once_with("/templates/1")

    @pytest.mark.asyncio
    async def test_get_by_alias(self, templates):
        manager, fake = templates
        fake.mock_get_response(TEMPLATE)

        await manager.get("welcome")

        fake.get.assert_called_once_with("/templates/welcome")

    @pytest.mark.asyncio
    async def test_response_fields_parsed(self, templates):
        manager, fake = templates
        fake.mock_get_response(TEMPLATE)

        result = await manager.get(1)

        assert result.subject == "Hello {{name}}"
        assert result.html_body == "<p>Hello {{name}}</p>"
        assert result.template_type == TemplateType.STANDARD
        assert result.active is True


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreateTemplate:
    @pytest.mark.asyncio
    async def test_dict_input(self, templates):
        manager, fake = templates
        fake.mock_post_response(UPSERT_RESPONSE)

        result = await manager.create({"Name": "Welcome", "Subject": "Hello"})

        assert result.template_id == 1
        fake.post.assert_called_once()
        assert fake.post.call_args[0][0] == "/templates"

    @pytest.mark.asyncio
    async def test_model_input(self, templates):
        manager, fake = templates
        fake.mock_post_response(UPSERT_RESPONSE)

        req = CreateTemplateRequest(**{"Name": "Welcome"})
        result = await manager.create(req)

        assert result.name == "Welcome"

    @pytest.mark.asyncio
    async def test_payload_uses_aliases(self, templates):
        manager, fake = templates
        fake.mock_post_response(UPSERT_RESPONSE)

        await manager.create({"Name": "Welcome", "HtmlBody": "<p>Hi</p>"})

        payload = fake.post.call_args[1]["json"]
        assert "Name" in payload
        assert "HtmlBody" in payload


# ---------------------------------------------------------------------------
# edit
# ---------------------------------------------------------------------------


class TestEditTemplate:
    @pytest.mark.asyncio
    async def test_edit_by_id(self, templates):
        manager, fake = templates
        fake.mock_put_response(UPSERT_RESPONSE)

        result = await manager.edit(1, {"Name": "Updated Welcome"})

        assert result.template_id == 1
        fake.put.assert_called_once()
        assert fake.put.call_args[0][0] == "/templates/1"

    @pytest.mark.asyncio
    async def test_edit_by_alias(self, templates):
        manager, fake = templates
        fake.mock_put_response(UPSERT_RESPONSE)

        await manager.edit("welcome", {"Name": "Updated Welcome"})

        assert fake.put.call_args[0][0] == "/templates/welcome"

    @pytest.mark.asyncio
    async def test_model_input(self, templates):
        manager, fake = templates
        fake.mock_put_response(UPSERT_RESPONSE)

        req = EditTemplateRequest(**{"Name": "Updated"})
        await manager.edit(1, req)

        payload = fake.put.call_args[1]["json"]
        assert payload["Name"] == "Updated"


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


class TestListTemplates:
    @pytest.fixture
    def list_response(self):
        return {
            "TotalCount": 2,
            "Templates": [
                TEMPLATE_SUMMARY,
                {
                    **TEMPLATE_SUMMARY,
                    "TemplateId": 2,
                    "Name": "Goodbye",
                    "Alias": "goodbye",
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_default_params(self, templates):
        manager, fake = templates
        fake.mock_get_response({"TotalCount": 0, "Templates": []})

        await manager.list()

        fake.get.assert_called_once_with(
            "/templates", params={"count": 100, "offset": 0}
        )

    @pytest.mark.asyncio
    async def test_returns_page(self, templates, list_response):
        manager, fake = templates
        fake.mock_get_response(list_response)

        result = await manager.list()

        assert result.total == 2
        assert len(result.items) == 2
        assert result.items[0].template_id == 1
        assert result.items[1].name == "Goodbye"

    @pytest.mark.asyncio
    async def test_with_template_type_filter(self, templates):
        manager, fake = templates
        fake.mock_get_response({"TotalCount": 0, "Templates": []})

        await manager.list(template_type=TemplateTypeFilter.STANDARD)

        params = fake.get.call_args[1]["params"]
        assert params["templateType"] == "Standard"

    @pytest.mark.asyncio
    async def test_with_layout_filter(self, templates):
        manager, fake = templates
        fake.mock_get_response({"TotalCount": 0, "Templates": []})

        await manager.list(count=50, offset=10, template_type=TemplateTypeFilter.LAYOUT)

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 50
        assert params["offset"] == 10
        assert params["templateType"] == "Layout"

    @pytest.mark.asyncio
    async def test_count_too_large_raises(self, templates):
        manager, fake = templates

        with pytest.raises(ValueError, match="500"):
            await manager.list(count=501)

        fake.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_count_plus_offset_too_large_raises(self, templates):
        manager, fake = templates

        with pytest.raises(ValueError, match="10,000"):
            await manager.list(count=500, offset=9_501)

        fake.get.assert_not_called()


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDeleteTemplate:
    @pytest.mark.asyncio
    async def test_delete_by_id(self, templates):
        manager, fake = templates
        fake.mock_delete_response(DELETE_RESPONSE)

        result = await manager.delete(1)

        assert result.error_code == 0
        assert result.message == "Template removed."
        fake.delete.assert_called_once_with("/templates/1")

    @pytest.mark.asyncio
    async def test_delete_by_alias(self, templates):
        manager, fake = templates
        fake.mock_delete_response(DELETE_RESPONSE)

        await manager.delete("welcome")

        fake.delete.assert_called_once_with("/templates/welcome")


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


class TestValidateTemplate:
    @pytest.mark.asyncio
    async def test_validate_dict_input(self, templates):
        manager, fake = templates
        fake.mock_post_response(VALIDATE_RESPONSE)

        result = await manager.validate(
            {
                "Subject": "Hello {{name}}",
                "HtmlBody": "<p>Hello {{name}}</p>",
                "TestRenderModel": {"name": "World"},
            }
        )

        assert result.all_content_is_valid is True
        fake.post.assert_called_once()
        assert fake.post.call_args[0][0] == "/templates/validate"

    @pytest.mark.asyncio
    async def test_validate_model_input(self, templates):
        manager, fake = templates
        fake.mock_post_response(VALIDATE_RESPONSE)

        req = ValidateTemplateRequest(**{"Subject": "Hello"})
        result = await manager.validate(req)

        assert result.all_content_is_valid is True

    @pytest.mark.asyncio
    async def test_validate_response_fields(self, templates):
        manager, fake = templates
        fake.mock_post_response(VALIDATE_RESPONSE)

        result = await manager.validate({"Subject": "Hello"})

        assert result.html_body is not None
        assert result.html_body.content_is_valid is True
        assert result.html_body.rendered_content == "<p>Hello World</p>"
        assert result.text_body is not None
        assert result.suggested_template_model == {"name": "World"}

    @pytest.mark.asyncio
    async def test_validate_with_errors(self, templates):
        manager, fake = templates
        error_response = {
            "AllContentIsValid": False,
            "HtmlBody": {
                "ContentIsValid": False,
                "ValidationErrors": [
                    {"Message": "Unclosed tag", "Line": 3, "CharacterPosition": 5}
                ],
                "RenderedContent": None,
            },
            "TextBody": None,
            "Subject": None,
            "SuggestedTemplateModel": None,
        }
        fake.mock_post_response(error_response)

        result = await manager.validate({"HtmlBody": "<p>{{unclosed"})

        assert result.all_content_is_valid is False
        assert len(result.html_body.validation_errors) == 1
        assert result.html_body.validation_errors[0].message == "Unclosed tag"
        assert result.html_body.validation_errors[0].line == 3


# ---------------------------------------------------------------------------
# push
# ---------------------------------------------------------------------------


class TestPushTemplates:
    @pytest.mark.asyncio
    async def test_push_dict_input(self, account_templates):
        manager, fake = account_templates
        fake.mock_put_response(PUSH_RESPONSE)

        result = await manager.push(
            {
                "SourceServerID": "src-123",
                "DestinationServerID": "dst-456",
                "PerformChanges": True,
            }
        )

        assert result.total_count == 1
        assert len(result.templates) == 1
        fake.put.assert_called_once()
        assert fake.put.call_args[0][0] == "/templates/push"

    @pytest.mark.asyncio
    async def test_push_model_input(self, account_templates):
        manager, fake = account_templates
        fake.mock_put_response(PUSH_RESPONSE)

        req = PushTemplatesRequest(
            **{
                "SourceServerID": "src-123",
                "DestinationServerID": "dst-456",
                "PerformChanges": False,
            }
        )
        result = await manager.push(req)

        assert result.templates[0].name == "Welcome"

    @pytest.mark.asyncio
    async def test_push_response_parsed(self, account_templates):
        manager, fake = account_templates
        fake.mock_put_response(PUSH_RESPONSE)

        result = await manager.push(
            {
                "SourceServerID": "src-123",
                "DestinationServerID": "dst-456",
                "PerformChanges": True,
            }
        )

        pushed = result.templates[0]
        assert pushed.alias == "welcome"
        assert pushed.template_type == TemplateType.STANDARD
