# Agents & Tools — lat-long-mcp-server

This repo is a scaffold for an MCP server that will expose tools around latitude/longitude utilities (e.g., resolving place names, validating coordinates, or proxying other geo services). Fill in the details as you build the server.

## Overview ✅
- Planned MCP server exposing geo-centric tools (to be implemented).
- Recommended to follow the same patterns used in `weather-mcp-server` for tool registration, retries, and diagnostics.

## Running the MCP server 🛠️
- Placeholder: add your server entrypoint (e.g., `python -m lat_long_mcp_server` or a `main.py`).
- Prefer `uv` for running: `uv run --with mcp python -m lat_long_mcp_server` once the module exists.
- Configure transport via env vars (suggested): `LAT_LONG_TRANSPORT`, `LAT_LONG_HOST`, `LAT_LONG_PORT`, `LAT_LONG_MOUNT_PATH`.

## Tooling
- Use `uv` to manage dependencies and stay aligned with lockfiles.
- Add tests with `pytest` and lint with `ruff` (recommended).

## Suggested tools (to implement) 🧭
- `validate_coordinates(latitude, longitude)` → basic bounds check.
- `reverse_geocode(latitude, longitude)` → resolve to nearest place (backed by your chosen API).
- `forward_geocode(query)` → search for lat/long by place name.
- Add unit tests with lightweight fakes/mocks for network calls.

## File format / diagnostics 📝
- If you persist lookups, include a small header with timestamp, inputs, and diagnostic fields (attempts, provider, latency).

## Extending the project ⚡
- Register new MCP tools with `mcp.tool()` and mirror the testing approach from `weather-mcp-server`.
- Document any required env vars (e.g., API keys) in this file and `.env.example`.

---
Concise, practical, and targeted at contributors building or debugging the upcoming geo tools.
