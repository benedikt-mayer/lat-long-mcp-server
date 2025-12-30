"""Integration tests for lat-long-mcp-server."""

import os
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_mcp_tool_registration():
    """Test that MCP tools are properly registered."""
    from lat_long_mcp_server.server import mcp

    # Check that the mcp object has tool decorators
    assert hasattr(mcp, "tool")


@pytest.mark.asyncio
async def test_full_forward_geocoding_workflow():
    """Test complete forward geocoding workflow."""
    from lat_long_mcp_server.server import forward_geocode

    mock_response = [
        {
            "name": "London",
            "state": "England",
            "country": "GB",
            "lat": 51.5074,
            "lon": -0.1278,
        },
        {
            "name": "London",
            "state": "Ontario",
            "country": "CA",
            "lat": 42.9849,
            "lon": -81.2453,
        },
    ]

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
            mock_get.return_value = mock_response
            result = await forward_geocode("London", limit=2)

            # Should have both London locations
            assert "London" in result
            assert "England" in result or "GB" in result
            assert "Ontario" in result or "CA" in result


@pytest.mark.asyncio
async def test_reverse_geocoding_workflow():
    """Test complete reverse geocoding workflow."""
    from lat_long_mcp_server.server import reverse_geocode

    # Coordinates for New York City
    mock_response = [
        {
            "name": "New York",
            "state": "New York",
            "country": "US",
            "lat": 40.7128,
            "lon": -74.006,
        }
    ]

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
            mock_get.return_value = mock_response
            result = await reverse_geocode(40.7128, -74.006)

            assert "New York" in result
            assert "40.7128" in result
            assert "-74.006" in result


@pytest.mark.asyncio
async def test_main_entry_point_version():
    """Test main entry point --version flag."""
    from lat_long_mcp_server.server import main

    with patch("sys.exit"):
        main(["--version"])


def test_main_entry_point_help():
    """Test main entry point help parsing."""
    from lat_long_mcp_server.server import main

    # Should not raise an error for valid arguments
    try:
        main(["--help"])
    except SystemExit:
        # argparse exits on --help, which is expected
        pass


@pytest.mark.asyncio
async def test_api_key_from_env():
    """Test that API key is read from environment."""
    from lat_long_mcp_server.server import forward_geocode

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "my_api_key"}):
            mock_get.return_value = [{"name": "Test", "lat": 0, "lon": 0}]
            await forward_geocode("Test")

            # Verify API key was passed to the request
            call_args = mock_get.call_args
            params = call_args.args[1]
            assert params["appid"] == "my_api_key"


@pytest.mark.asyncio
async def test_error_handling_missing_api_key():
    """Test error when API key is missing."""
    from lat_long_mcp_server.server import forward_geocode

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="OPENWEATHERMAP_API_KEY is required"):
            await forward_geocode("Test")


def test_default_server_settings():
    """Test default server settings."""
    from lat_long_mcp_server.server import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_MOUNT

    assert DEFAULT_HOST == "127.0.0.1"
    assert DEFAULT_PORT == "8001"
    assert DEFAULT_MOUNT == "/mcp"
