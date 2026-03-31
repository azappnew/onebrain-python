"""Tests for onebrain.resources.brain (sync + async)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.brain import AsyncBrainResource, BrainResource


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def mock_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def resource(mock_client: MagicMock) -> BrainResource:
    return BrainResource(mock_client)


@pytest.fixture()
def async_mock_client() -> MagicMock:
    client = MagicMock()
    client.request = AsyncMock()
    return client


@pytest.fixture()
def async_resource(async_mock_client: MagicMock) -> AsyncBrainResource:
    return AsyncBrainResource(async_mock_client)


# ── Sync: profile ─────────────────────────────────────────────────────


class TestBrainProfile:
    """Tests for BrainResource.profile()."""

    def test_profile_returns_data(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        expected = {
            "summary": "A curious developer",
            "traits": {"curiosity": 0.9},
            "preferences": {"language": "en"},
        }
        mock_client.request.return_value = expected
        result = resource.profile()
        mock_client.request.assert_called_once_with(
            "GET", "/v1/brain/profile"
        )
        assert result == expected

    def test_profile_correct_method_and_path(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.profile()
        args, kwargs = mock_client.request.call_args
        assert args == ("GET", "/v1/brain/profile")
        assert kwargs == {}


# ── Sync: update_profile ──────────────────────────────────────────────


class TestBrainUpdateProfile:
    """Tests for BrainResource.update_profile()."""

    def test_update_summary_only(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        mock_client.request.return_value = {"summary": "Updated"}
        result = resource.update_profile(summary="Updated")
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/brain/profile",
            json={"summary": "Updated"},
        )
        assert result["summary"] == "Updated"

    def test_update_traits_only(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        traits = {"openness": 0.8, "detail_oriented": True}
        mock_client.request.return_value = {"traits": traits}
        resource.update_profile(traits=traits)
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/brain/profile",
            json={"traits": traits},
        )

    def test_update_preferences_only(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        prefs = {"theme": "dark", "language": "de"}
        mock_client.request.return_value = {}
        resource.update_profile(preferences=prefs)
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/brain/profile",
            json={"preferences": prefs},
        )

    def test_update_all_fields(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.update_profile(
            summary="New summary",
            traits={"fast": True},
            preferences={"tz": "UTC"},
        )
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/brain/profile",
            json={
                "summary": "New summary",
                "traits": {"fast": True},
                "preferences": {"tz": "UTC"},
            },
        )

    def test_update_empty_payload_when_no_args(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.update_profile()
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/brain/profile", json={}
        )

    def test_update_omits_none_fields(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.update_profile(
            summary="Yes", traits=None, preferences=None
        )
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/brain/profile",
            json={"summary": "Yes"},
        )

    def test_update_uses_put_method(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.update_profile(summary="Check method")
        args, _ = mock_client.request.call_args
        assert args[0] == "PUT"


# ── Sync: context ─────────────────────────────────────────────────────


class TestBrainContext:
    """Tests for BrainResource.context()."""

    def test_context_returns_full_context(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        expected = {
            "formatted": "Context text...",
            "structured": {"memory_count": 42},
            "meta": {"tokenEstimate": 1500},
        }
        mock_client.request.return_value = expected
        result = resource.context()
        mock_client.request.assert_called_once_with(
            "GET", "/v1/brain/context"
        )
        assert result == expected

    def test_context_correct_method_and_path(
        self, mock_client: MagicMock, resource: BrainResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.context()
        args, kwargs = mock_client.request.call_args
        assert args == ("GET", "/v1/brain/context")
        assert kwargs == {}


# ═══════════════════════════════════════════════════════════════════════
# Async variants
# ═══════════════════════════════════════════════════════════════════════


class TestAsyncBrainProfile:
    """Tests for AsyncBrainResource.profile()."""

    @pytest.mark.asyncio()
    async def test_profile(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncBrainResource,
    ) -> None:
        expected = {"summary": "Async brain"}
        async_mock_client.request.return_value = expected
        result = await async_resource.profile()
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/brain/profile"
        )
        assert result == expected


class TestAsyncBrainUpdateProfile:
    """Tests for AsyncBrainResource.update_profile()."""

    @pytest.mark.asyncio()
    async def test_update_summary(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncBrainResource,
    ) -> None:
        async_mock_client.request.return_value = {"summary": "Async"}
        await async_resource.update_profile(summary="Async")
        async_mock_client.request.assert_awaited_once_with(
            "PUT",
            "/v1/brain/profile",
            json={"summary": "Async"},
        )

    @pytest.mark.asyncio()
    async def test_update_all_fields(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncBrainResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.update_profile(
            summary="S",
            traits={"a": 1},
            preferences={"b": 2},
        )
        async_mock_client.request.assert_awaited_once_with(
            "PUT",
            "/v1/brain/profile",
            json={
                "summary": "S",
                "traits": {"a": 1},
                "preferences": {"b": 2},
            },
        )

    @pytest.mark.asyncio()
    async def test_update_empty(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncBrainResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.update_profile()
        async_mock_client.request.assert_awaited_once_with(
            "PUT", "/v1/brain/profile", json={}
        )


class TestAsyncBrainContext:
    """Tests for AsyncBrainResource.context()."""

    @pytest.mark.asyncio()
    async def test_context(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncBrainResource,
    ) -> None:
        expected = {"formatted": "Async context"}
        async_mock_client.request.return_value = expected
        result = await async_resource.context()
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/brain/context"
        )
        assert result == expected
