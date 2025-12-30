"""Basic MCP server exposing OpenWeather geocoding tools."""

import argparse
import json
import os
from typing import Any, Dict, List

import httpx

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - fallback for environments without mcp
    class FastMCP:  # type: ignore
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def tool(self):
            def _dec(f):
                return f

            return _dec

        def run(self, *args: Any, **kwargs: Any) -> None:
            return None


API_BASE = "https://api.openweathermap.org/geo/1.0"
DEFAULT_HOST = os.environ.get("LAT_LONG_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("LAT_LONG_PORT", "8000"))
DEFAULT_MOUNT = os.environ.get("LAT_LONG_MOUNT_PATH", "/mcp")

mcp = FastMCP(
    "lat-long",
    host=DEFAULT_HOST,
    port=DEFAULT_PORT,
    mount_path=DEFAULT_MOUNT,
    streamable_http_path=DEFAULT_MOUNT,
)


def _require_api_key() -> str:
    key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not key:
        raise RuntimeError("OPENWEATHERMAP_API_KEY is required for geocoding requests.")
    return key


async def _get_json(path: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    url = f"{API_BASE}/{path}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def _format_locations(records: List[Dict[str, Any]]) -> str:
    if not records:
        return "No locations found."

    lines = []
    for idx, item in enumerate(records, start=1):
        name = item.get("name") or "Unknown"
        state = item.get("state")
        country = item.get("country") or "?"
        lat = item.get("lat")
        lon = item.get("lon")
        extra_parts = []
        if state:
            extra_parts.append(str(state))
        if country:
            extra_parts.append(str(country))
        meta = ", ".join(extra_parts)
        meta_part = f" ({meta})" if meta else ""
        lines.append(f"{idx}. {name}{meta_part} -> lat={lat}, lon={lon}")

    return "\n".join(lines)


@mcp.tool()
async def forward_geocode(query: str, limit: int = 1, country_code: str | None = None) -> str:
    """Resolve a place name to latitude/longitude using OpenWeather Geocoding."""
    key = _require_api_key()
    limit = max(1, min(limit, 5))
    q = query.strip()
    if country_code:
        q = f"{q},{country_code.strip()}"

    records = await _get_json("direct", {"q": q, "limit": limit, "appid": key})
    return _format_locations(records)


@mcp.tool()
async def reverse_geocode(latitude: float, longitude: float, limit: int = 1) -> str:
    """Resolve latitude/longitude to the nearest places using OpenWeather Geocoding."""
    key = _require_api_key()
    limit = max(1, min(limit, 5))
    records = await _get_json(
        "reverse",
        {"lat": latitude, "lon": longitude, "limit": limit, "appid": key},
    )
    return _format_locations(records)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="lat-long-mcp-server")
    parser.add_argument("command", nargs="?", choices=["run"], default="run")
    parser.add_argument("--version", action="store_true", help="Print package version and exit")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default=os.environ.get("LAT_LONG_TRANSPORT", "streamable-http"),
        help="Transport to use (default: streamable-http)",
    )
    parser.add_argument(
        "--mount-path",
        default=os.environ.get("LAT_LONG_MOUNT_PATH", "/mcp"),
        help="Mount path for HTTP transports (default: /mcp)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("LAT_LONG_HOST", "127.0.0.1"),
        help="Host to bind the HTTP server to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("LAT_LONG_PORT", "8000")),
        help="Port to bind the HTTP server to",
    )
    parser.add_argument(
        "--api-key",
        help="OpenWeatherMap API key (overrides OPENWEATHERMAP_API_KEY env var)",
    )
    args = parser.parse_args(argv)

    if args.version:
        try:
            from importlib.metadata import version

            print(version("lat-long-mcp-server"))
        except Exception:
            print("version unknown")
        return

    if args.api_key:
        os.environ["OPENWEATHERMAP_API_KEY"] = args.api_key

    if args.command == "run":
        # Host/port are configured on FastMCP at construction time via env vars.
        mcp.run(transport=args.transport, mount_path=args.mount_path)


if __name__ == "__main__":
    main()
