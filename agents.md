# Agents & Tools — lat-long-mcp-server

This repo hosts an MCP server that exposes OpenWeather Geocoding tools for latitude/longitude lookups.

## Overview ✅
- MCP server exposing geo-centric tools backed by OpenWeather Geocoding.
- Patterned after `weather-mcp-server` for FastMCP setup and HTTP transport defaults.

## Running the MCP server 🛠️
- Start: `uv run --with mcp python -m lat_long_mcp_server --transport streamable-http --host 127.0.0.1 --port 8000 --mount-path /mcp`
- StdIO: `uv run --with mcp python -m lat_long_mcp_server --transport stdio`
- Configure via env vars: `LAT_LONG_TRANSPORT`, `LAT_LONG_HOST`, `LAT_LONG_PORT`, `LAT_LONG_MOUNT_PATH`, and `OPENWEATHERMAP_API_KEY`.

## Tooling
- Use `uv` to manage dependencies and stay aligned with lockfiles.
- Add tests with `pytest` and lint with `ruff` (recommended).
- **After every code change, run:** `ruff check --fix .` and `ruff format .` to ensure code quality and consistency.
- **Commit and push separately:** run `git commit` first, then `git push` as separate steps (avoid chaining commit+push).
- Always ask before pushing to any remote.

## Current tools 🧭
- `forward_geocode(query, limit=1, country_code=None)` → OpenWeather direct geocoding.
- `reverse_geocode(latitude, longitude, limit=1)` → OpenWeather reverse geocoding.

## File format / diagnostics 📝
- If you persist lookups, include a small header with timestamp, inputs, and diagnostic fields (attempts, provider, latency).

## Extending the project ⚡
- Register new MCP tools with `mcp.tool()` and mirror the testing approach from `weather-mcp-server`.
- Document any required env vars (e.g., API keys) in this file and `.env.example`.

---
Concise, practical, and targeted at contributors building or debugging the upcoming geo tools.
