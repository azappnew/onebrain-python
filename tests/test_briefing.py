"""Tests for onebrain.resources.briefing — BriefingResource & AsyncBriefingResource."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.briefing import AsyncBriefingResource, BriefingResource


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_client():
    """Return a MagicMock that mimics BaseClient."""
    client = MagicMock()
    client.request.return_value = {}
    client.request_paginated.return_value = {
        "items": [],
        "cursor": None,
        "has_more": False,
        "total": 0,
    }
    return client


@pytest.fixture()
def resource(mock_client):
    return BriefingResource(mock_client)


@pytest.fixture()
def async_mock_client():
    """Return an AsyncMock that mimics AsyncBaseClient."""
    client = AsyncMock()
    client.request.return_value = {}
    client.request_paginated.return_value = {
        "items": [],
        "cursor": None,
        "has_more": False,
        "total": 0,
    }
    return client


@pytest.fixture()
def async_resource(async_mock_client):
    return AsyncBriefingResource(async_mock_client)


# ===================================================================
# Sync — BriefingResource.config
# ===================================================================


class TestBriefingConfig:
    """Tests for BriefingResource.config()."""

    def test_config_calls_correct_endpoint(self, resource, mock_client):
        resource.config()

        mock_client.request.assert_called_once_with(
            "GET", "/v1/briefings/config",
        )

    def test_config_returns_full_config(self, resource, mock_client):
        config_data = {
            "id": "cfg_1",
            "is_enabled": True,
            "timezone": "Europe/Berlin",
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "07:00",
            "channels": ["email", "push"],
        }
        mock_client.request.return_value = config_data

        result = resource.config()

        assert result == config_data
        assert result["is_enabled"] is True
        assert result["timezone"] == "Europe/Berlin"

    def test_config_returns_disabled_config(self, resource, mock_client):
        mock_client.request.return_value = {
            "id": "cfg_2",
            "is_enabled": False,
            "timezone": "UTC",
            "quiet_hours_start": None,
            "quiet_hours_end": None,
            "channels": [],
        }

        result = resource.config()

        assert result["is_enabled"] is False
        assert result["channels"] == []


# ===================================================================
# Sync — BriefingResource.list
# ===================================================================


class TestBriefingList:
    """Tests for BriefingResource.list()."""

    def test_list_no_params(self, resource, mock_client):
        result = resource.list()

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/briefings", params={},
        )
        assert result == mock_client.request_paginated.return_value

    def test_list_with_type_filter(self, resource, mock_client):
        resource.list(type="morning")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/briefings", params={"type": "morning"},
        )

    def test_list_with_status_filter(self, resource, mock_client):
        resource.list(status="ready")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/briefings", params={"status": "ready"},
        )

    def test_list_with_pagination(self, resource, mock_client):
        resource.list(cursor="cur_abc", limit=5)

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/briefings",
            params={"cursor": "cur_abc", "limit": 5},
        )

    def test_list_with_all_params(self, resource, mock_client):
        resource.list(
            type="evening",
            status="delivered",
            cursor="page3",
            limit=15,
        )

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/briefings",
            params={
                "type": "evening",
                "status": "delivered",
                "cursor": "page3",
                "limit": 15,
            },
        )

    def test_list_returns_paginated_items(self, resource, mock_client):
        expected = {
            "items": [
                {
                    "id": "br_1",
                    "type": "morning",
                    "status": "ready",
                    "title": "Morning Briefing",
                    "created_at": "2026-03-31T07:00:00Z",
                },
            ],
            "cursor": "next_cur",
            "has_more": True,
            "total": 100,
        }
        mock_client.request_paginated.return_value = expected

        result = resource.list()

        assert len(result["items"]) == 1
        assert result["items"][0]["type"] == "morning"
        assert result["has_more"] is True

    @pytest.mark.parametrize(
        "briefing_type",
        ["morning", "midday", "evening", "event_triggered", "weekly_health"],
    )
    def test_list_all_briefing_types(
        self, resource, mock_client, briefing_type
    ):
        resource.list(type=briefing_type)

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/briefings",
            params={"type": briefing_type},
        )

    @pytest.mark.parametrize(
        "status",
        ["pending", "generating", "ready", "delivered", "failed"],
    )
    def test_list_all_status_values(self, resource, mock_client, status):
        resource.list(status=status)

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/briefings",
            params={"status": status},
        )

    def test_list_none_params_excluded(self, resource, mock_client):
        """Params set to None must not appear in the request dict."""
        resource.list(type=None, status=None, cursor=None, limit=None)

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/briefings", params={},
        )


# ===================================================================
# Async — AsyncBriefingResource.config
# ===================================================================


class TestAsyncBriefingConfig:
    """Tests for AsyncBriefingResource.config()."""

    @pytest.mark.asyncio
    async def test_config_calls_correct_endpoint(
        self, async_resource, async_mock_client
    ):
        await async_resource.config()

        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/briefings/config",
        )

    @pytest.mark.asyncio
    async def test_config_returns_data(
        self, async_resource, async_mock_client
    ):
        async_mock_client.request.return_value = {
            "id": "cfg_a",
            "is_enabled": True,
            "timezone": "America/New_York",
            "quiet_hours_start": None,
            "quiet_hours_end": None,
            "channels": ["slack"],
        }

        result = await async_resource.config()

        assert result["timezone"] == "America/New_York"
        assert result["channels"] == ["slack"]


# ===================================================================
# Async — AsyncBriefingResource.list
# ===================================================================


class TestAsyncBriefingList:
    """Tests for AsyncBriefingResource.list()."""

    @pytest.mark.asyncio
    async def test_list_no_params(
        self, async_resource, async_mock_client
    ):
        result = await async_resource.list()

        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET", "/v1/briefings", params={},
        )
        assert result == async_mock_client.request_paginated.return_value

    @pytest.mark.asyncio
    async def test_list_with_all_params(
        self, async_resource, async_mock_client
    ):
        await async_resource.list(
            type="weekly_health",
            status="pending",
            cursor="async_cur",
            limit=30,
        )

        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET",
            "/v1/briefings",
            params={
                "type": "weekly_health",
                "status": "pending",
                "cursor": "async_cur",
                "limit": 30,
            },
        )

    @pytest.mark.asyncio
    async def test_list_returns_paginated_result(
        self, async_resource, async_mock_client
    ):
        expected = {
            "items": [{"id": "br_async_1"}],
            "cursor": None,
            "has_more": False,
            "total": 1,
        }
        async_mock_client.request_paginated.return_value = expected

        result = await async_resource.list()

        assert result["items"] == [{"id": "br_async_1"}]
        assert result["has_more"] is False
