"""Basic MCP server exposing OpenWeather geocoding tools."""

import argparse
from importlib.metadata import version
import os
from typing import Any, Dict, List

import anyio
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

API_BASE = "https://api.openweathermap.org/geo/1.0"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8001
DEFAULT_MOUNT = "/mcp"

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
async def forward_geocode(
    query: str, limit: int = 1, country_code: str | None = None
) -> str:
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
    parser.add_argument(
        "--version", action="store_true", help="Print package version and exit"
    )
    args = parser.parse_args(argv)

    if args.version:
        try:
            print(version("lat-long-mcp-server"))
        except Exception:
            print("version unknown")
        return

    anyio.run(mcp.run_streamable_http_async)


if __name__ == "__main__":
    main()
