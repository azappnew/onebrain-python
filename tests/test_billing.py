"""Tests for onebrain.resources.billing — BillingResource & AsyncBillingResource."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.billing import AsyncBillingResource, BillingResource


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_client():
    """Return a MagicMock that mimics BaseClient."""
    client = MagicMock()
    client.request.return_value = {}
    return client


@pytest.fixture()
def resource(mock_client):
    return BillingResource(mock_client)


@pytest.fixture()
def async_mock_client():
    """Return an AsyncMock that mimics AsyncBaseClient."""
    client = AsyncMock()
    client.request.return_value = {}
    return client


@pytest.fixture()
def async_resource(async_mock_client):
    return AsyncBillingResource(async_mock_client)


# ===================================================================
# Sync — BillingResource.usage
# ===================================================================


class TestBillingUsage:
    """Tests for BillingResource.usage()."""

    def test_usage_no_params(self, resource, mock_client):
        resource.usage()

        mock_client.request.assert_called_once_with(
            "GET", "/v1/billing/usage", params={},
        )

    def test_usage_with_period(self, resource, mock_client):
        resource.usage(period="daily")

        mock_client.request.assert_called_once_with(
            "GET", "/v1/billing/usage", params={"period": "daily"},
        )

    @pytest.mark.parametrize("period", ["daily", "weekly", "monthly"])
    def test_usage_all_periods(self, resource, mock_client, period):
        resource.usage(period=period)

        mock_client.request.assert_called_once_with(
            "GET", "/v1/billing/usage", params={"period": period},
        )

    def test_usage_returns_stats(self, resource, mock_client):
        expected = {
            "period": "2026-03",
            "usage": {
                "memory_writes": 1500,
                "memory_reads": 12000,
                "search_queries": 800,
                "ai_extractions": 200,
            },
        }
        mock_client.request.return_value = expected

        result = resource.usage()

        assert result["period"] == "2026-03"
        assert result["usage"]["memory_writes"] == 1500

    def test_usage_none_period_excluded(self, resource, mock_client):
        """Explicitly passing period=None should not include it."""
        resource.usage(period=None)

        mock_client.request.assert_called_once_with(
            "GET", "/v1/billing/usage", params={},
        )


# ===================================================================
# Sync — BillingResource.plan
# ===================================================================


class TestBillingPlan:
    """Tests for BillingResource.plan()."""

    def test_plan_calls_correct_endpoint(self, resource, mock_client):
        resource.plan()

        mock_client.request.assert_called_once_with(
            "GET", "/v1/billing/plan",
        )

    def test_plan_returns_details(self, resource, mock_client):
        expected = {
            "name": "Pro",
            "limits": {
                "memory_items": 100000,
                "api_calls_per_month": 500000,
                "ai_extractions_per_month": 10000,
            },
        }
        mock_client.request.return_value = expected

        result = resource.plan()

        assert result["name"] == "Pro"
        assert result["limits"]["memory_items"] == 100000

    def test_plan_returns_free_tier(self, resource, mock_client):
        mock_client.request.return_value = {
            "name": "Free",
            "limits": {
                "memory_items": 1000,
                "api_calls_per_month": 10000,
            },
        }

        result = resource.plan()

        assert result["name"] == "Free"


# ===================================================================
# Async — AsyncBillingResource.usage
# ===================================================================


class TestAsyncBillingUsage:
    """Tests for AsyncBillingResource.usage()."""

    @pytest.mark.asyncio
    async def test_usage_no_params(
        self, async_resource, async_mock_client
    ):
        await async_resource.usage()

        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/billing/usage", params={},
        )

    @pytest.mark.asyncio
    async def test_usage_with_period(
        self, async_resource, async_mock_client
    ):
        await async_resource.usage(period="weekly")

        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/billing/usage", params={"period": "weekly"},
        )

    @pytest.mark.asyncio
    async def test_usage_returns_data(
        self, async_resource, async_mock_client
    ):
        async_mock_client.request.return_value = {
            "period": "2026-W13",
            "usage": {"memory_writes": 300},
        }

        result = await async_resource.usage(period="weekly")

        assert result["period"] == "2026-W13"


# ===================================================================
# Async — AsyncBillingResource.plan
# ===================================================================


class TestAsyncBillingPlan:
    """Tests for AsyncBillingResource.plan()."""

    @pytest.mark.asyncio
    async def test_plan_calls_correct_endpoint(
        self, async_resource, async_mock_client
    ):
        await async_resource.plan()

        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/billing/plan",
        )

    @pytest.mark.asyncio
    async def test_plan_returns_data(
        self, async_resource, async_mock_client
    ):
        async_mock_client.request.return_value = {
            "name": "Enterprise",
            "limits": {"memory_items": 1000000},
        }

        result = await async_resource.plan()

        assert result["name"] == "Enterprise"
        assert result["limits"]["memory_items"] == 1000000
