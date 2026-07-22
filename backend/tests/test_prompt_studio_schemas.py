import pytest
from pydantic import ValidationError

from app.schemas.prompt_studio import (
    MAX_VARIABLES,
    PromptCreate,
    PromptUpdateContent,
    PromptUpdateMeta,
)

VAR = {"name": "audience", "type": "string", "required": True}


def test_create_accepts_a_body_whose_placeholders_are_all_declared():
    prompt = PromptCreate(name="Summary", body="Write for ${audience}.", variables=[VAR])
    assert prompt.variables[0].name == "audience"


def test_create_rejects_undeclared_placeholder():
    with pytest.raises(ValidationError, match="undeclared"):
        PromptCreate(name="Summary", body="Write for ${audience}.", variables=[])


def test_create_rejects_duplicate_variable_names():
    with pytest.raises(ValidationError, match="unique"):
        PromptCreate(name="X", body="${a}", variables=[{"name": "a", "type": "string"}, {"name": "a", "type": "number"}])


def test_create_rejects_more_than_max_variables():
    variables = [{"name": f"v{i}", "type": "string"} for i in range(MAX_VARIABLES + 1)]
    body = " ".join(f"${{v{i}}}" for i in range(MAX_VARIABLES + 1))
    with pytest.raises(ValidationError, match="at most"):
        PromptCreate(name="X", body=body, variables=variables)


def test_create_rejects_invalid_variable_name_pattern():
    with pytest.raises(ValidationError):
        PromptCreate(name="X", body="${1bad}", variables=[{"name": "1bad", "type": "string"}])


def test_create_rejects_too_many_tags():
    with pytest.raises(ValidationError, match="at most"):
        PromptCreate(name="X", body="hi", tags=[f"tag{i}" for i in range(11)])


def test_create_accepts_escaped_dollar_without_requiring_a_variable():
    prompt = PromptCreate(name="X", body="Cost is $$5.", variables=[])
    assert prompt.body == "Cost is $$5."


def test_update_content_rejects_undeclared_placeholder_same_as_create():
    with pytest.raises(ValidationError, match="undeclared"):
        PromptUpdateContent(body="${typo}", variables=[])


def test_update_meta_allows_partial_payload():
    meta = PromptUpdateMeta(name="New name")
    assert meta.name == "New name"
    assert meta.description is None
    assert meta.tags is None
