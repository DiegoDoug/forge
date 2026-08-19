"""MCP tool handlers (Phase 11, Milestone 2 onward). Each submodule owns one
Forge domain (notes, documents, projects, ...) and exposes a
``register(server)`` function that attaches its tools via ``server.tool()``.
``app/mcp/server.py::build_mcp_server`` calls each domain's ``register()`` -
a flat, explicit wiring list, not a dynamic plugin-discovery system (per
01_SPEC.md SS7, a flat registry is sufficient at this tool count)."""
