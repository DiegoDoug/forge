"""
RC Audit for Prompt Studio — Stage 4 (Release Candidate).

Systematically verifies every requirement from 01_SPEC.md §3 and 08_ACCEPTANCE.md
against the actual implementation. Tests are designed to falsify assumptions and
classify findings as BLOCKER/MAJOR/MINOR/OBSERVATION per 12_BUG_CLASSIFICATION.md.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime

import pytest


@pytest.fixture(scope="module")
def audit_client():
    """Isolated test client for RC audit - mirrors test_prompt_studio_api.py."""
    from app.core.config import get_settings
    from app.database.session import get_engine, get_sessionmaker

    previous_data_dir = os.environ.get("FORGE_DATA_DIR")
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    os.environ["FORGE_DATA_DIR"] = tempfile.mkdtemp(prefix="forge-rc-audit-")

    from app.main import create_app
    from starlette.testclient import TestClient

    app = create_app()
    with TestClient(app) as c:
        c.post("/api/setup", json={"master_password": "audit-test"})
        yield c

    if previous_data_dir is None:
        os.environ.pop("FORGE_DATA_DIR", None)
    else:
        os.environ["FORGE_DATA_DIR"] = previous_data_dir
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


# ============================================================================
# §3.1–3.3: Prompt Creation and Variables
# ============================================================================


def test_req_3_1_create_prompt_with_all_fields(audit_client):
    """§3.1-3.3: Create a prompt with name, description, tags, body, and variables."""
    payload = {
        "name": "Code Review Prompt",
        "description": "Rubric for reviewing code quality.",
        "body": "Review this code for ${criteria}. Focus on ${aspect}.",
        "variables": [
            {"name": "criteria", "type": "string", "required": True, "description": "Review criteria"},
            {"name": "aspect", "type": "string", "required": False, "default": "correctness"},
        ],
        "tags": ["review", "code"],
    }
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 201, f"Create failed: {response.text}"
    data = response.json()
    assert data["name"] == "Code Review Prompt"
    assert data["description"] == "Rubric for reviewing code quality."
    assert len(data["variables"]) == 2
    assert data["tags"] == ["review", "code"]
    assert data["version_number"] == 1, "New prompt should start at version 1"
    print("✓ §3.1-3.3: Prompt creation with all fields works")


def test_req_3_3_variable_name_pattern_validation(audit_client):
    """§3.3: Variable name must match ^[A-Za-z_][A-Za-z0-9_]{0,63}$"""
    # Invalid: starts with digit
    payload = {
        "name": "Test",
        "body": "Test ${1invalid}",
        "variables": [{"name": "1invalid", "type": "string", "required": True}],
    }
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Should reject variable name starting with digit"

    # Invalid: contains hyphen
    payload["variables"][0]["name"] = "invalid-name"
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Should reject variable name with hyphen"

    # Valid: underscore and numbers after first char
    payload["variables"][0]["name"] = "_valid_123"
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 201, "Should accept valid identifier"
    print("✓ §3.3: Variable name pattern validation works")


def test_req_3_3_variable_uniqueness(audit_client):
    """§3.3: Variable names must be unique within a prompt."""
    payload = {
        "name": "Duplicate Vars",
        "body": "Use ${var} and ${var}",
        "variables": [
            {"name": "var", "type": "string", "required": True},
            {"name": "var", "type": "string", "required": True},  # Duplicate
        ],
    }
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Should reject duplicate variable names"
    print("✓ §3.3: Variable uniqueness enforced")


def test_req_3_3_max_50_variables(audit_client):
    """§3.3: A prompt may declare at most 50 variables."""
    # Create exactly 50 variables
    variables_50 = [
        {"name": f"var_{i:02d}", "type": "string", "required": False} for i in range(50)
    ]
    body = "".join([f"${{{v['name']}}}" for v in variables_50])
    payload = {"name": "Max Vars", "body": body, "variables": variables_50}
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 201, "Should accept exactly 50 variables"

    # Try 51 variables
    variables_51 = variables_50 + [{"name": "var_50", "type": "string", "required": False}]
    body = "".join([f"${{{v['name']}}}" for v in variables_51])
    payload = {"name": "Too Many Vars", "body": body, "variables": variables_51}
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Should reject more than 50 variables"
    print("✓ §3.3: 50-variable limit enforced")


# ============================================================================
# §3.4: Placeholder Validation
# ============================================================================


def test_req_3_4_undeclared_placeholder_rejected(audit_client):
    """§3.4: Saving a body that references undeclared ${name} is rejected with 422."""
    payload = {
        "name": "Undeclared Placeholder",
        "body": "Use ${declared} and ${undeclared}.",
        "variables": [{"name": "declared", "type": "string", "required": True}],
    }
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Should reject undeclared placeholder"
    assert "undeclared" in response.text.lower() or "placeholder" in response.text.lower()
    print("✓ §3.4: Undeclared placeholder rejected")


def test_req_3_4_all_declared_succeeds(audit_client):
    """§3.4: Saving a body whose every ${name} is declared succeeds."""
    payload = {
        "name": "All Declared",
        "body": "Use ${var1} and ${var2} and ${var1}.",  # var1 can be referenced multiple times
        "variables": [
            {"name": "var1", "type": "string", "required": True},
            {"name": "var2", "type": "string", "required": True},
        ],
    }
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 201, "Should accept all-declared body"
    print("✓ §3.4: All-declared body succeeds")


def test_req_3_4_escaped_dollar_not_placeholder(audit_client):
    """§3.4: A literal $$ is not treated as placeholder, doesn't require variable."""
    payload = {
        "name": "Escaped Dollar",
        "body": "Use $$100 as price.",  # $$ should escape to literal $
        "variables": [],  # No variables needed
    }
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 201, "Should accept escaped $$ without variable"
    print("✓ §3.4: Escaped $$ handled correctly")


# ============================================================================
# §3.7: Versioning
# ============================================================================


def test_req_3_7_body_change_creates_new_version(audit_client):
    """§3.7: Changing body creates new version; version counter increments."""
    # Create initial prompt
    create_payload = {
        "name": "Version Test",
        "body": "Original body.",
        "variables": [],
    }
    create_resp = audit_client.post("/api/prompts", json=create_payload)
    assert create_resp.status_code == 201
    prompt_id = create_resp.json()["id"]
    assert create_resp.json()["version_number"] == 1

    # Update body
    update_payload = {"body": "Updated body.", "variables": []}
    update_resp = audit_client.put(f"/api/prompts/{prompt_id}/content", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["version_number"] == 2, "Body change should bump version"

    # Verify first version still exists
    versions_resp = audit_client.get(f"/api/prompts/{prompt_id}/versions")
    assert versions_resp.status_code == 200
    assert len(versions_resp.json()["items"]) == 2, "Should have 2 versions"
    print("✓ §3.7: Body change creates new version")


def test_req_3_7_variables_change_creates_new_version(audit_client):
    """§3.7: Changing variables creates new version; version counter increments."""
    create_payload = {
        "name": "Var Version Test",
        "body": "${original}",
        "variables": [{"name": "original", "type": "string", "required": True}],
    }
    create_resp = audit_client.post("/api/prompts", json=create_payload)
    prompt_id = create_resp.json()["id"]
    assert create_resp.json()["version_number"] == 1

    # Update variables
    update_payload = {
        "body": "${updated}",
        "variables": [{"name": "updated", "type": "string", "required": True}],
    }
    update_resp = audit_client.put(f"/api/prompts/{prompt_id}/content", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["version_number"] == 2, "Variable change should bump version"
    print("✓ §3.7: Variable change creates new version")


def test_req_3_7_metadata_change_no_version(audit_client):
    """§3.7: Changing name/description/tags does NOT create new version."""
    create_payload = {
        "name": "Meta Test",
        "body": "Body.",
        "variables": [],
    }
    create_resp = audit_client.post("/api/prompts", json=create_payload)
    prompt_id = create_resp.json()["id"]
    v1 = create_resp.json()["version_number"]

    # Update only metadata
    meta_payload = {"name": "Meta Test Renamed"}
    meta_resp = audit_client.patch(f"/api/prompts/{prompt_id}", json=meta_payload)
    assert meta_resp.status_code == 200
    assert meta_resp.json()["version_number"] == v1, "Metadata change should NOT bump version"

    # Verify only 1 version exists
    versions_resp = audit_client.get(f"/api/prompts/{prompt_id}/versions")
    assert len(versions_resp.json()["items"]) == 1, "Should still have only 1 version"
    print("✓ §3.7: Metadata change does not create version")


# ============================================================================
# §3.9: Restore
# ============================================================================


def test_req_3_9_restore_snapshots_current_first(audit_client):
    """§3.9: Restoring version N snapshots current content, never reuses version number."""
    # Create v1
    create_payload = {
        "name": "Restore Test",
        "body": "v1",
        "variables": [],
    }
    create_resp = audit_client.post("/api/prompts", json=create_payload)
    prompt_id = create_resp.json()["id"]
    v1_id = None
    for v in audit_client.get(f"/api/prompts/{prompt_id}/versions").json()["items"]:
        if v["version_number"] == 1:
            v1_id = v["id"]

    # Edit to v2
    audit_client.put(f"/api/prompts/{prompt_id}/content", json={"body": "v2", "variables": []})

    # Edit to v3
    audit_client.put(f"/api/prompts/{prompt_id}/content", json={"body": "v3", "variables": []})
    assert audit_client.get(f"/api/prompts/{prompt_id}").json()["version_number"] == 3

    # Restore v1 - should create v4 with v1's content
    restore_resp = audit_client.post(f"/api/prompts/{prompt_id}/versions/{v1_id}/restore")
    assert restore_resp.status_code == 200
    assert restore_resp.json()["version_number"] == 4, "Restore should create new version"
    assert restore_resp.json()["body"] == "v1", "Content should match v1"

    # Verify all versions exist
    versions = audit_client.get(f"/api/prompts/{prompt_id}/versions").json()["items"]
    version_numbers = [v["version_number"] for v in versions]
    assert version_numbers == [4, 3, 2, 1], f"Should have [4,3,2,1], got {version_numbers}"
    print("✓ §3.9: Restore snapshots current and never reuses version number")


# ============================================================================
# §3.10: Duplicate
# ============================================================================


def test_req_3_10_duplicate_creates_independent_prompt(audit_client):
    """§3.10: Duplicate creates independent prompt with own id, copies body/variables/tags."""
    # Create source
    create_payload = {
        "name": "Original",
        "description": "Original desc",
        "body": "Original ${var}",
        "variables": [{"name": "var", "type": "string", "required": True}],
        "tags": ["original"],
    }
    create_resp = audit_client.post("/api/prompts", json=create_payload)
    source_id = create_resp.json()["id"]

    # Duplicate
    dup_resp = audit_client.post(f"/api/prompts/{source_id}/duplicate")
    assert dup_resp.status_code == 201
    dup_data = dup_resp.json()

    # Verify independence
    assert dup_data["id"] != source_id, "Duplicate should have different id"
    assert dup_data["name"] == "Original (copy)", "Name should have (copy) suffix"
    assert dup_data["description"] == "Original desc", "Description should be copied"
    assert dup_data["body"] == "Original ${var}", "Body should be copied"
    assert dup_data["variables"][0]["name"] == "var", "Variables should be copied"
    assert dup_data["tags"] == ["original"], "Tags should be copied"
    assert dup_data["version_number"] == 1, "Duplicate should start at v1"

    # Verify duplicate has only v1
    dup_versions = audit_client.get(f"/api/prompts/{dup_data['id']}/versions").json()
    assert len(dup_versions["items"]) == 1, "Duplicate should have only v1"
    print("✓ §3.10: Duplicate creates independent prompt")


def test_req_3_10_duplicate_survives_source_deletion(audit_client):
    """§3.10: Duplicate is fully independent; survives source deletion."""
    # Create source
    source_resp = audit_client.post("/api/prompts", json={"name": "Source", "body": "Test"})
    source_id = source_resp.json()["id"]

    # Duplicate
    dup_resp = audit_client.post(f"/api/prompts/{source_id}/duplicate")
    dup_id = dup_resp.json()["id"]

    # Delete source
    del_resp = audit_client.delete(f"/api/prompts/{source_id}")
    assert del_resp.status_code == 204

    # Verify duplicate still exists
    dup_still_exists = audit_client.get(f"/api/prompts/{dup_id}")
    assert dup_still_exists.status_code == 200, "Duplicate should survive source deletion"
    print("✓ §3.10: Duplicate survives source deletion")


# ============================================================================
# §3.12: Delete
# ============================================================================


def test_req_3_12_delete_cascades_to_versions(audit_client):
    """§3.12: Deleting a prompt cascades to delete all of its versions."""
    # Create prompt with multiple versions
    create_resp = audit_client.post("/api/prompts", json={"name": "Delete Test", "body": "v1"})
    prompt_id = create_resp.json()["id"]

    # Create v2 and v3
    audit_client.put(f"/api/prompts/{prompt_id}/content", json={"body": "v2", "variables": []})
    audit_client.put(f"/api/prompts/{prompt_id}/content", json={"body": "v3", "variables": []})

    # Verify 3 versions exist
    versions_before = audit_client.get(f"/api/prompts/{prompt_id}/versions").json()
    assert len(versions_before["items"]) == 3

    # Delete prompt
    del_resp = audit_client.delete(f"/api/prompts/{prompt_id}")
    assert del_resp.status_code == 204

    # Verify prompt returns 404
    get_resp = audit_client.get(f"/api/prompts/{prompt_id}")
    assert get_resp.status_code == 404, "Deleted prompt should return 404"

    # Verify versions also return 404
    versions_resp = audit_client.get(f"/api/prompts/{prompt_id}/versions")
    assert versions_resp.status_code == 404, "Versions should also return 404 after prompt deletion"
    print("✓ §3.12: Delete cascades to versions")


# ============================================================================
# §3.13: Activity Logging (Core verification)
# ============================================================================
# Note: Full activity logging tests are already in test_prompt_studio_api.py
# This is a sanity check that the API endpoints don't error on the main actions.


def test_req_3_13_activity_logging_no_errors(audit_client):
    """§3.13: Core operations (create/update/restore/duplicate/delete) don't error."""
    # Create
    create_resp = audit_client.post("/api/prompts", json={"name": "Activity Test", "body": "test"})
    assert create_resp.status_code == 201, "Create should succeed"
    prompt_id = create_resp.json()["id"]

    # Update content
    update_resp = audit_client.put(f"/api/prompts/{prompt_id}/content", json={"body": "updated", "variables": []})
    assert update_resp.status_code == 200, "Update should succeed"

    # Restore
    versions = audit_client.get(f"/api/prompts/{prompt_id}/versions").json()
    v1_id = [v["id"] for v in versions["items"] if v["version_number"] == 1][0]
    restore_resp = audit_client.post(f"/api/prompts/{prompt_id}/versions/{v1_id}/restore")
    assert restore_resp.status_code == 200, "Restore should succeed"

    # Duplicate
    dup_resp = audit_client.post(f"/api/prompts/{prompt_id}/duplicate")
    assert dup_resp.status_code == 201, "Duplicate should succeed"

    # Delete
    del_resp = audit_client.delete(f"/api/prompts/{prompt_id}")
    assert del_resp.status_code == 204, "Delete should succeed"

    print("✓ §3.13: Activity logging operations complete without error")


# ============================================================================
# §3.16: Rendering Determinism
# ============================================================================


def test_req_3_16_no_eval_in_templating(audit_client):
    """§3.16: Templating module has no eval/exec/template engine."""
    import ast
    from app.services.prompt_studio import templating

    # Read the source code
    import inspect
    source = inspect.getsource(templating)

    # Parse as AST
    tree = ast.parse(source)

    # Check for eval, exec, compile, etc.
    forbidden_names = {"eval", "exec", "compile", "format_map", "format", "f-string"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in forbidden_names:
                raise AssertionError(f"Found forbidden call: {node.func.id}")

    print("✓ §3.16: Templating module is eval-free")


def test_req_3_16_only_substitution_escaping_validation():
    """§3.16: Templating only does substitution, escaping, validation."""
    from app.services.prompt_studio.templating import extract_placeholders, substitute

    # Test substitution
    result = substitute("Hello ${name}", {"name": "Alice"})
    assert result == "Hello Alice"

    # Test escaping
    result = substitute("Cost: $$100", {})
    assert result == "Cost: $100"

    # Test validation (missing key raises KeyError)
    try:
        substitute("Hello ${missing}", {})
        assert False, "Should raise KeyError for missing variable"
    except KeyError:
        pass

    # Test extraction
    placeholders = extract_placeholders("Use ${var1} and ${var2} with $$escaped")
    assert placeholders == {"var1", "var2"}

    print("✓ §3.16: Templating is deterministic (substitution + escaping + validation)")


# ============================================================================
# Integration: Field Limits
# ============================================================================


def test_integration_field_length_limits(audit_client):
    """Integration: All field length limits from §3."""
    # Name: 1–200 chars
    payload = {"name": "", "body": "test"}
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Empty name should be rejected"

    payload["name"] = "x" * 201
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Name > 200 should be rejected"

    # Description: ≤1000 chars
    payload["name"] = "Test"
    payload["description"] = "x" * 1001
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Description > 1000 should be rejected"

    # Body: 1–20,000 chars
    payload["description"] = "OK"
    payload["body"] = ""
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Empty body should be rejected"

    payload["body"] = "x" * 20001
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Body > 20,000 should be rejected"

    # Tags: ≤10 tags, each ≤30 chars
    payload["body"] = "test"
    payload["tags"] = ["a"] * 11
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "More than 10 tags should be rejected"

    payload["tags"] = ["x" * 31]
    response = audit_client.post("/api/prompts", json=payload)
    assert response.status_code == 422, "Tag > 30 chars should be rejected"

    print("✓ Integration: Field length limits enforced")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
