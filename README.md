# lat-long-mcp-server

An MCP server that exposes OpenWeather Geocoding tools for forward and reverse lookups.

## Setup
- Requires Python 3.12+.
- Install with uv (preferred): `uv sync` or `uv pip install -e .`.
- Set an API key: `export OPENWEATHERMAP_API_KEY=...` (or pass `--api-key`).

## Run
- Default HTTP endpoint: `uv run --with mcp python -m lat_long_mcp_server --transport streamable-http --host 127.0.0.1 --port 8000 --mount-path /mcp`
- StdIO: `uv run --with mcp python -m lat_long_mcp_server --transport stdio`

## Tools
- `forward_geocode(query, limit=1, country_code=None)`
- `reverse_geocode(latitude, longitude, limit=1)`

## Env vars
- `OPENWEATHERMAP_API_KEY` (required)
- `LAT_LONG_TRANSPORT` (default `streamable-http`)
- `LAT_LONG_HOST` (default `127.0.0.1`)
- `LAT_LONG_PORT` (default `8000`)
- `LAT_LONG_MOUNT_PATH` (default `/mcp`)
