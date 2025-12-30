"""Unit tests for lat_long_mcp_server.server module."""

import os
import pytest
from unittest.mock import AsyncMock, patch


def test_format_locations_empty():
    """Test formatting empty location list."""
    from lat_long_mcp_server.server import _format_locations

    result = _format_locations([])
    assert result == "No locations found."


def test_format_locations_single():
    """Test formatting a single location."""
    from lat_long_mcp_server.server import _format_locations

    records = [
        {
            "name": "Berlin",
            "state": "Berlin",
            "country": "DE",
            "lat": 52.52,
            "lon": 13.405,
        }
    ]
    result = _format_locations(records)

    assert "1. Berlin (Berlin, DE) -> lat=52.52, lon=13.405" in result


def test_format_locations_multiple():
    """Test formatting multiple locations."""
    from lat_long_mcp_server.server import _format_locations

    records = [
        {
            "name": "Berlin",
            "state": "Berlin",
            "country": "DE",
            "lat": 52.52,
            "lon": 13.405,
        },
        {"name": "Paris", "state": None, "country": "FR", "lat": 48.856, "lon": 2.352},
    ]
    result = _format_locations(records)

    assert "1. Berlin (Berlin, DE)" in result
    assert "2. Paris (FR)" in result


def test_format_locations_missing_fields():
    """Test formatting locations with missing optional fields."""
    from lat_long_mcp_server.server import _format_locations

    records = [{"name": "Unknown Place", "lat": 0.0, "lon": 0.0}]
    result = _format_locations(records)

    assert "1. Unknown Place (?) -> lat=0.0, lon=0.0" in result


def test_require_api_key_present():
    """Test API key requirement when key is set."""
    from lat_long_mcp_server.server import _require_api_key

    with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
        key = _require_api_key()
        assert key == "test_key"


def test_require_api_key_missing():
    """Test API key requirement when key is not set."""
    from lat_long_mcp_server.server import _require_api_key

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="OPENWEATHERMAP_API_KEY is required"):
            _require_api_key()


@pytest.mark.asyncio
async def test_forward_geocode_success():
    """Test successful forward geocoding."""
    from lat_long_mcp_server.server import forward_geocode

    mock_response = [
        {
            "name": "Berlin",
            "state": "Berlin",
            "country": "DE",
            "lat": 52.52,
            "lon": 13.405,
        }
    ]

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
            mock_get.return_value = mock_response
            result = await forward_geocode("Berlin", limit=1)

            assert "Berlin" in result
            assert "52.52" in result
            assert "13.405" in result
            mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_forward_geocode_with_country():
    """Test forward geocoding with country code."""
    from lat_long_mcp_server.server import forward_geocode

    mock_response = [
        {
            "name": "Paris",
            "state": None,
            "country": "FR",
            "lat": 48.856,
            "lon": 2.352,
        }
    ]

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
            mock_get.return_value = mock_response
            result = await forward_geocode("Paris", country_code="FR")

            assert "Paris" in result
            assert "FR" in result
            # Verify query was formatted with country code
            call_args = mock_get.call_args
            assert call_args.args[0] == "direct"
            params = call_args.args[1]
            assert "FR" in params["q"]


@pytest.mark.asyncio
async def test_forward_geocode_limit_clamping():
    """Test that limit is clamped between 1 and 5."""
    from lat_long_mcp_server.server import forward_geocode

    mock_response = [{"name": "Berlin", "country": "DE", "lat": 52.52, "lon": 13.405}]

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
            mock_get.return_value = mock_response

            # Test with limit > 5
            await forward_geocode("Berlin", limit=10)
            call_args = mock_get.call_args
            params = call_args.args[1]
            assert params["limit"] == 5

            # Test with limit < 1
            await forward_geocode("Berlin", limit=0)
            call_args = mock_get.call_args
            params = call_args.args[1]
            assert params["limit"] == 1


@pytest.mark.asyncio
async def test_reverse_geocode_success():
    """Test successful reverse geocoding."""
    from lat_long_mcp_server.server import reverse_geocode

    mock_response = [
        {
            "name": "Berlin",
            "state": "Berlin",
            "country": "DE",
            "lat": 52.52,
            "lon": 13.405,
        }
    ]

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
            mock_get.return_value = mock_response
            result = await reverse_geocode(52.52, 13.405)

            assert "Berlin" in result
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args.args[0] == "reverse"
            params = call_args.args[1]
            assert params["lat"] == 52.52
            assert params["lon"] == 13.405


@pytest.mark.asyncio
async def test_forward_geocode_no_results():
    """Test forward geocoding with no results."""
    from lat_long_mcp_server.server import forward_geocode

    with patch(
        "lat_long_mcp_server.server._get_json", new_callable=AsyncMock
    ) as mock_get:
        with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
            mock_get.return_value = []
            result = await forward_geocode("NonExistentPlace")

            assert result == "No locations found."


def test_api_base_url():
    """Test that API base URL is correct."""
    from lat_long_mcp_server.server import API_BASE

    assert API_BASE == "https://api.openweathermap.org/geo/1.0"
