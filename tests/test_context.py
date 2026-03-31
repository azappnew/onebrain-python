"""Tests for onebrain.resources.context (sync + async)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.context import AsyncContextResource, ContextResource


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def mock_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def resource(mock_client: MagicMock) -> ContextResource:
    return ContextResource(mock_client)


@pytest.fixture()
def async_mock_client() -> MagicMock:
    client = MagicMock()
    client.request = AsyncMock()
    return client


@pytest.fixture()
def async_resource(
    async_mock_client: MagicMock,
) -> AsyncContextResource:
    return AsyncContextResource(async_mock_client)


# ── Sync: get with default scope ─────────────────────────────────────


class TestContextGetDefault:
    """Tests for ContextResource.get() with default scope."""

    def test_get_default_scope_is_deep(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        mock_client.request.return_value = {
            "formatted": "Full context",
            "meta": {"tokenEstimate": 5000},
        }
        result = resource.get()
        mock_client.request.assert_called_once_with(
            "GET", "/v1/context/deep"
        )
        assert result["formatted"] == "Full context"

    def test_get_default_returns_mock_data(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        expected = {"structured": {"items": 10}}
        mock_client.request.return_value = expected
        result = resource.get()
        assert result is expected


# ── Sync: get with explicit scopes ───────────────────────────────────


class TestContextGetScopes:
    """Tests for ContextResource.get() with all scope values."""

    def test_get_scope_brief(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        mock_client.request.return_value = {"formatted": "Brief"}
        result = resource.get("brief")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/context/brief"
        )
        assert result["formatted"] == "Brief"

    def test_get_scope_assistant(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        mock_client.request.return_value = {"formatted": "Assistant"}
        resource.get("assistant")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/context/assistant"
        )

    def test_get_scope_project(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        mock_client.request.return_value = {
            "formatted": "Project-scoped context",
        }
        resource.get("project")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/context/project"
        )

    def test_get_scope_deep(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        mock_client.request.return_value = {"formatted": "Deep"}
        resource.get("deep")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/context/deep"
        )


# ── Sync: URL encoding ───────────────────────────────────────────────


class TestContextGetUrlEncoding:
    """Tests for scope URL encoding in ContextResource.get()."""

    def test_scope_with_slash_is_encoded(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.get("a/b")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/context/a%2Fb"
        )

    def test_scope_with_space_is_encoded(
        self, mock_client: MagicMock, resource: ContextResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.get("my scope")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/context/my%20scope"
        )


# ═══════════════════════════════════════════════════════════════════════
# Async variants
# ═══════════════════════════════════════════════════════════════════════


class TestAsyncContextGetDefault:
    """Tests for AsyncContextResource.get() with default scope."""

    @pytest.mark.asyncio()
    async def test_get_default_scope(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncContextResource,
    ) -> None:
        expected = {"formatted": "Async deep context"}
        async_mock_client.request.return_value = expected
        result = await async_resource.get()
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/context/deep"
        )
        assert result == expected


class TestAsyncContextGetScopes:
    """Tests for AsyncContextResource.get() with all scope values."""

    @pytest.mark.asyncio()
    async def test_get_scope_brief(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncContextResource,
    ) -> None:
        async_mock_client.request.return_value = {"formatted": "Brief"}
        await async_resource.get("brief")
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/context/brief"
        )

    @pytest.mark.asyncio()
    async def test_get_scope_assistant(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncContextResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.get("assistant")
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/context/assistant"
        )

    @pytest.mark.asyncio()
    async def test_get_scope_project(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncContextResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.get("project")
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/context/project"
        )

    @pytest.mark.asyncio()
    async def test_get_scope_deep_explicit(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncContextResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.get("deep")
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/context/deep"
        )
