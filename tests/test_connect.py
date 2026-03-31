"""Tests for onebrain.resources.connect (sync + async)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.connect import AsyncConnectResource, ConnectResource


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def mock_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def resource(mock_client: MagicMock) -> ConnectResource:
    return ConnectResource(mock_client)


@pytest.fixture()
def async_mock_client() -> MagicMock:
    client = MagicMock()
    client.request = AsyncMock()
    return client


@pytest.fixture()
def async_resource(
    async_mock_client: MagicMock,
) -> AsyncConnectResource:
    return AsyncConnectResource(async_mock_client)


# ── Sync: read ────────────────────────────────────────────────────────


class TestConnectRead:
    """Tests for ConnectResource.read()."""

    def test_read_no_params(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        expected = {"context": "full data"}
        mock_client.request.return_value = expected
        result = resource.read()
        mock_client.request.assert_called_once_with(
            "GET", "/v1/connect", params={}
        )
        assert result == expected

    def test_read_with_scope(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.read(scope="brief")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/connect", params={"scope": "brief"}
        )

    def test_read_with_format(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.read(format="json")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/connect", params={"format": "json"}
        )

    def test_read_with_scope_and_format(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {"formatted": "text"}
        result = resource.read(scope="deep", format="text")
        mock_client.request.assert_called_once_with(
            "GET",
            "/v1/connect",
            params={"scope": "deep", "format": "text"},
        )
        assert result["formatted"] == "text"

    def test_read_omits_none_params(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.read(scope=None, format=None)
        mock_client.request.assert_called_once_with(
            "GET", "/v1/connect", params={}
        )


# ── Sync: write_memory ───────────────────────────────────────────────


class TestConnectWriteMemory:
    """Tests for ConnectResource.write_memory()."""

    def test_write_memory_required_fields(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        expected = {"status": "created", "id": "mem_1"}
        mock_client.request.return_value = expected
        result = resource.write_memory(
            "fact", "Python expertise", "10 years of Python"
        )
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/connect/memory",
            json={
                "type": "fact",
                "title": "Python expertise",
                "body": "10 years of Python",
            },
        )
        assert result["status"] == "created"

    def test_write_memory_with_source_type(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {"id": "mem_2"}
        resource.write_memory(
            "preference",
            "Dark mode",
            "Prefers dark themes",
            source_type="user_input",
        )
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/connect/memory",
            json={
                "type": "preference",
                "title": "Dark mode",
                "body": "Prefers dark themes",
                "sourceType": "user_input",
            },
        )

    def test_write_memory_omits_none_source_type(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.write_memory(
            "goal", "Learn Rust", "Start in Q2", source_type=None
        )
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/connect/memory",
            json={
                "type": "goal",
                "title": "Learn Rust",
                "body": "Start in Q2",
            },
        )

    def test_write_memory_all_types(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        """Verify different memory types pass through correctly."""
        for mem_type in [
            "fact",
            "preference",
            "decision",
            "goal",
            "experience",
            "skill",
        ]:
            mock_client.reset_mock()
            mock_client.request.return_value = {"id": f"m_{mem_type}"}
            resource.write_memory(mem_type, "Title", "Body")
            mock_client.request.assert_called_once_with(
                "POST",
                "/v1/connect/memory",
                json={
                    "type": mem_type,
                    "title": "Title",
                    "body": "Body",
                },
            )


# ── Sync: write_memories (batch) ─────────────────────────────────────


class TestConnectWriteMemories:
    """Tests for ConnectResource.write_memories()."""

    def test_write_memories_single_item(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        items = [
            {"type": "fact", "title": "T1", "body": "B1"},
        ]
        expected = {"created": 1, "duplicates": 0, "results": []}
        mock_client.request.return_value = expected
        result = resource.write_memories(items)
        mock_client.request.assert_called_once_with(
            "POST", "/v1/connect/memories", json=items
        )
        assert result["created"] == 1

    def test_write_memories_multiple_items(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        items = [
            {"type": "fact", "title": "T1", "body": "B1"},
            {"type": "skill", "title": "T2", "body": "B2"},
            {"type": "goal", "title": "T3", "body": "B3"},
        ]
        mock_client.request.return_value = {
            "created": 2,
            "duplicates": 1,
        }
        result = resource.write_memories(items)
        mock_client.request.assert_called_once_with(
            "POST", "/v1/connect/memories", json=items
        )
        assert result["created"] == 2
        assert result["duplicates"] == 1

    def test_write_memories_empty_list(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {
            "created": 0,
            "duplicates": 0,
        }
        result = resource.write_memories([])
        mock_client.request.assert_called_once_with(
            "POST", "/v1/connect/memories", json=[]
        )
        assert result["created"] == 0


# ── Sync: delta ───────────────────────────────────────────────────────


class TestConnectDelta:
    """Tests for ConnectResource.delta()."""

    def test_delta_with_timestamp(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        expected = {
            "changes": [{"id": "c1", "action": "created"}],
            "count": 1,
        }
        mock_client.request.return_value = expected
        result = resource.delta("2026-01-15T09:30:00Z")
        mock_client.request.assert_called_once_with(
            "GET",
            "/v1/connect/delta",
            params={"since": "2026-01-15T09:30:00Z"},
        )
        assert result["count"] == 1

    def test_delta_returns_empty_changes(
        self, mock_client: MagicMock, resource: ConnectResource
    ) -> None:
        mock_client.request.return_value = {"changes": [], "count": 0}
        result = resource.delta("2026-03-31T00:00:00Z")
        mock_client.request.assert_called_once_with(
            "GET",
            "/v1/connect/delta",
            params={"since": "2026-03-31T00:00:00Z"},
        )
        assert result["changes"] == []


# ═══════════════════════════════════════════════════════════════════════
# Async variants
# ═══════════════════════════════════════════════════════════════════════


class TestAsyncConnectRead:
    """Tests for AsyncConnectResource.read()."""

    @pytest.mark.asyncio()
    async def test_read_no_params(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncConnectResource,
    ) -> None:
        expected = {"context": "async data"}
        async_mock_client.request.return_value = expected
        result = await async_resource.read()
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/connect", params={}
        )
        assert result == expected

    @pytest.mark.asyncio()
    async def test_read_with_scope_and_format(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncConnectResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.read(scope="assistant", format="json")
        async_mock_client.request.assert_awaited_once_with(
            "GET",
            "/v1/connect",
            params={"scope": "assistant", "format": "json"},
        )


class TestAsyncConnectWriteMemory:
    """Tests for AsyncConnectResource.write_memory()."""

    @pytest.mark.asyncio()
    async def test_write_memory_required_fields(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncConnectResource,
    ) -> None:
        async_mock_client.request.return_value = {"id": "am_1"}
        result = await async_resource.write_memory(
            "experience", "Async coding", "Built async SDK"
        )
        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/connect/memory",
            json={
                "type": "experience",
                "title": "Async coding",
                "body": "Built async SDK",
            },
        )
        assert result["id"] == "am_1"

    @pytest.mark.asyncio()
    async def test_write_memory_with_source_type(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncConnectResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.write_memory(
            "decision",
            "Use pytest",
            "Chose pytest over unittest",
            source_type="ai_extraction",
        )
        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/connect/memory",
            json={
                "type": "decision",
                "title": "Use pytest",
                "body": "Chose pytest over unittest",
                "sourceType": "ai_extraction",
            },
        )


class TestAsyncConnectWriteMemories:
    """Tests for AsyncConnectResource.write_memories()."""

    @pytest.mark.asyncio()
    async def test_write_memories_batch(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncConnectResource,
    ) -> None:
        items = [
            {"type": "fact", "title": "T1", "body": "B1"},
            {"type": "skill", "title": "T2", "body": "B2"},
        ]
        async_mock_client.request.return_value = {
            "created": 2,
            "duplicates": 0,
        }
        result = await async_resource.write_memories(items)
        async_mock_client.request.assert_awaited_once_with(
            "POST", "/v1/connect/memories", json=items
        )
        assert result["created"] == 2


class TestAsyncConnectDelta:
    """Tests for AsyncConnectResource.delta()."""

    @pytest.mark.asyncio()
    async def test_delta(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncConnectResource,
    ) -> None:
        expected = {"changes": [{"id": "ac1"}], "count": 1}
        async_mock_client.request.return_value = expected
        result = await async_resource.delta("2026-01-01T00:00:00Z")
        async_mock_client.request.assert_awaited_once_with(
            "GET",
            "/v1/connect/delta",
            params={"since": "2026-01-01T00:00:00Z"},
        )
        assert result["count"] == 1

    @pytest.mark.asyncio()
    async def test_delta_empty_result(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncConnectResource,
    ) -> None:
        async_mock_client.request.return_value = {
            "changes": [],
            "count": 0,
        }
        result = await async_resource.delta("2026-12-31T23:59:59Z")
        async_mock_client.request.assert_awaited_once_with(
            "GET",
            "/v1/connect/delta",
            params={"since": "2026-12-31T23:59:59Z"},
        )
        assert result["changes"] == []
