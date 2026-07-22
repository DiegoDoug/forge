import pytest

from app.services.prompt_studio.templating import extract_placeholders, substitute


def test_extract_placeholders_finds_named_variable():
    assert extract_placeholders("Hello ${name}!") == {"name"}


def test_extract_placeholders_dedupes_repeated_reference():
    assert extract_placeholders("${name}, is that really ${name}?") == {"name"}


def test_extract_placeholders_finds_multiple_distinct_names():
    assert extract_placeholders("${greeting} ${name}, from ${sender}.") == {"greeting", "name", "sender"}


def test_extract_placeholders_ignores_escaped_dollar():
    assert extract_placeholders("Cost is $$5, not a ${variable}.") == {"variable"}


def test_extract_placeholders_empty_body_yields_empty_set():
    assert extract_placeholders("No placeholders here.") == set()


def test_substitute_renders_declared_values():
    assert substitute("Hello ${name}!", {"name": "World"}) == "Hello World!"


def test_substitute_escapes_literal_dollar():
    assert substitute("Cost is $$5.", {}) == "Cost is $5."


def test_substitute_raises_on_missing_required_value():
    with pytest.raises(KeyError):
        substitute("Hello ${name}!", {})


def test_templating_module_has_no_expression_language():
    """Determinism constraint (01_SPEC.md §3.16): this module must never gain
    a conditional/loop/function-call/filter/include/import capability. This
    test parses the module's actual `import` statements (via `ast`, not a raw
    text search - the module's own docstring names `jinja2` as an example of
    what NOT to use) and asserts stdlib `string` is the only thing imported."""
    import ast

    import app.services.prompt_studio.templating as templating_module

    with open(templating_module.__file__, encoding="utf-8") as f:
        tree = ast.parse(f.read())

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert imported_modules == {"string", "__future__"}

    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert called_names.isdisjoint({"eval", "exec", "compile"})
