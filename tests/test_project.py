"""Tests for onebrain.resources.project (sync + async)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call

import pytest

from onebrain.resources.project import AsyncProjectResource, ProjectResource


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def mock_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def resource(mock_client: MagicMock) -> ProjectResource:
    return ProjectResource(mock_client)


@pytest.fixture()
def async_mock_client() -> MagicMock:
    client = MagicMock()
    client.request = AsyncMock()
    client.request_paginated = AsyncMock()
    return client


@pytest.fixture()
def async_resource(async_mock_client: MagicMock) -> AsyncProjectResource:
    return AsyncProjectResource(async_mock_client)


# ── Sync: list ────────────────────────────────────────────────────────


class TestProjectList:
    """Tests for ProjectResource.list()."""

    def test_list_no_params(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request_paginated.return_value = {
            "items": [],
            "cursor": None,
            "has_more": False,
            "total": 0,
        }
        result = resource.list()
        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/projects", params={}
        )
        assert result["items"] == []

    def test_list_with_status_filter(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request_paginated.return_value = {
            "items": [{"id": "p1", "status": "active"}],
            "cursor": None,
            "has_more": False,
            "total": 1,
        }
        result = resource.list(status="active")
        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/projects", params={"status": "active"}
        )
        assert len(result["items"]) == 1

    def test_list_with_cursor_pagination(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request_paginated.return_value = {
            "items": [{"id": "p2"}],
            "cursor": "next_abc",
            "has_more": True,
            "total": 50,
        }
        result = resource.list(cursor="abc123", limit=10)
        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/projects",
            params={"cursor": "abc123", "limit": 10},
        )
        assert result["has_more"] is True
        assert result["cursor"] == "next_abc"

    def test_list_with_all_params(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request_paginated.return_value = {
            "items": [],
            "cursor": None,
            "has_more": False,
            "total": 0,
        }
        resource.list(status="archived", cursor="cur_x", limit=50)
        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/projects",
            params={
                "status": "archived",
                "cursor": "cur_x",
                "limit": 50,
            },
        )

    def test_list_returns_mock_data(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        expected = {
            "items": [{"id": "p1"}, {"id": "p2"}],
            "cursor": "c2",
            "has_more": True,
            "total": 100,
        }
        mock_client.request_paginated.return_value = expected
        result = resource.list()
        assert result is expected


# ── Sync: get ─────────────────────────────────────────────────────────


class TestProjectGet:
    """Tests for ProjectResource.get()."""

    def test_get_by_id(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        expected = {"id": "proj_123", "name": "My Project"}
        mock_client.request.return_value = expected
        result = resource.get("proj_123")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/projects/proj_123"
        )
        assert result == expected

    def test_get_url_encodes_special_chars(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {"id": "a/b"}
        resource.get("a/b")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/projects/a%2Fb"
        )

    def test_get_url_encodes_spaces(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.get("my project")
        mock_client.request.assert_called_once_with(
            "GET", "/v1/projects/my%20project"
        )


# ── Sync: create ──────────────────────────────────────────────────────


class TestProjectCreate:
    """Tests for ProjectResource.create()."""

    def test_create_minimal(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        expected = {"id": "new_1", "name": "Test"}
        mock_client.request.return_value = expected
        result = resource.create("Test")
        mock_client.request.assert_called_once_with(
            "POST", "/v1/projects", json={"name": "Test"}
        )
        assert result == expected

    def test_create_with_all_fields(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        meta = {"priority": "high", "team": "backend"}
        mock_client.request.return_value = {"id": "new_2"}
        resource.create(
            "Full Project",
            status="active",
            description="A full project",
            metadata=meta,
        )
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/projects",
            json={
                "name": "Full Project",
                "status": "active",
                "description": "A full project",
                "metadata": meta,
            },
        )

    def test_create_omits_none_fields(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.create("Sparse", status=None, description=None)
        mock_client.request.assert_called_once_with(
            "POST", "/v1/projects", json={"name": "Sparse"}
        )

    def test_create_with_status_only(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.create("Proj", status="completed")
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/projects",
            json={"name": "Proj", "status": "completed"},
        )


# ── Sync: update ──────────────────────────────────────────────────────


class TestProjectUpdate:
    """Tests for ProjectResource.update()."""

    def test_update_name(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {
            "id": "p1",
            "name": "Renamed",
        }
        result = resource.update("p1", name="Renamed")
        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/projects/p1",
            json={"name": "Renamed"},
        )
        assert result["name"] == "Renamed"

    def test_update_status(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.update("p1", status="archived")
        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/projects/p1",
            json={"status": "archived"},
        )

    def test_update_all_fields(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        meta = {"v": 2}
        mock_client.request.return_value = {}
        resource.update(
            "p1",
            name="New",
            status="active",
            description="Desc",
            metadata=meta,
        )
        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/projects/p1",
            json={
                "name": "New",
                "status": "active",
                "description": "Desc",
                "metadata": meta,
            },
        )

    def test_update_omits_none_fields(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.update("p1")
        mock_client.request.assert_called_once_with(
            "PATCH", "/v1/projects/p1", json={}
        )

    def test_update_url_encodes_id(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.update("id/slash", name="X")
        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/projects/id%2Fslash",
            json={"name": "X"},
        )


# ── Sync: delete ──────────────────────────────────────────────────────


class TestProjectDelete:
    """Tests for ProjectResource.delete()."""

    def test_delete(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = None
        resource.delete("p1")
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/projects/p1"
        )

    def test_delete_url_encodes_id(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = None
        resource.delete("a b")
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/projects/a%20b"
        )


# ── Sync: add_memory_link ────────────────────────────────────────────


class TestProjectAddMemoryLink:
    """Tests for ProjectResource.add_memory_link()."""

    def test_add_memory_link(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        expected = {"id": "link_1", "projectId": "p1"}
        mock_client.request.return_value = expected
        result = resource.add_memory_link("p1", "mem_42", "reference")
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/projects/p1/memory-links",
            json={
                "memoryItemId": "mem_42",
                "linkType": "reference",
            },
        )
        assert result == expected

    def test_add_memory_link_url_encodes_project_id(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = {}
        resource.add_memory_link("p/1", "mem_1", "depends_on")
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/projects/p%2F1/memory-links",
            json={
                "memoryItemId": "mem_1",
                "linkType": "depends_on",
            },
        )


# ── Sync: remove_memory_link ─────────────────────────────────────────


class TestProjectRemoveMemoryLink:
    """Tests for ProjectResource.remove_memory_link()."""

    def test_remove_memory_link(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = None
        resource.remove_memory_link("p1", "link_99")
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/projects/p1/memory-links/link_99"
        )

    def test_remove_memory_link_url_encodes_both_ids(
        self, mock_client: MagicMock, resource: ProjectResource
    ) -> None:
        mock_client.request.return_value = None
        resource.remove_memory_link("p/1", "l/2")
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/projects/p%2F1/memory-links/l%2F2"
        )


# ═══════════════════════════════════════════════════════════════════════
# Async variants
# ═══════════════════════════════════════════════════════════════════════


class TestAsyncProjectList:
    """Tests for AsyncProjectResource.list()."""

    @pytest.mark.asyncio()
    async def test_list_no_params(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request_paginated.return_value = {
            "items": [],
            "cursor": None,
            "has_more": False,
            "total": 0,
        }
        result = await async_resource.list()
        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET", "/v1/projects", params={}
        )
        assert result["items"] == []

    @pytest.mark.asyncio()
    async def test_list_with_status(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request_paginated.return_value = {
            "items": [{"id": "p1"}],
            "cursor": None,
            "has_more": False,
            "total": 1,
        }
        await async_resource.list(status="active")
        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET", "/v1/projects", params={"status": "active"}
        )

    @pytest.mark.asyncio()
    async def test_list_with_pagination(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request_paginated.return_value = {
            "items": [],
            "cursor": "c2",
            "has_more": True,
            "total": 50,
        }
        result = await async_resource.list(cursor="c1", limit=25)
        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET",
            "/v1/projects",
            params={"cursor": "c1", "limit": 25},
        )
        assert result["has_more"] is True


class TestAsyncProjectGet:
    """Tests for AsyncProjectResource.get()."""

    @pytest.mark.asyncio()
    async def test_get_by_id(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        expected = {"id": "proj_abc", "name": "Async Proj"}
        async_mock_client.request.return_value = expected
        result = await async_resource.get("proj_abc")
        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/projects/proj_abc"
        )
        assert result == expected


class TestAsyncProjectCreate:
    """Tests for AsyncProjectResource.create()."""

    @pytest.mark.asyncio()
    async def test_create_minimal(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request.return_value = {"id": "new"}
        result = await async_resource.create("AsyncTest")
        async_mock_client.request.assert_awaited_once_with(
            "POST", "/v1/projects", json={"name": "AsyncTest"}
        )
        assert result["id"] == "new"

    @pytest.mark.asyncio()
    async def test_create_with_all_fields(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.create(
            "Full",
            status="active",
            description="Desc",
            metadata={"k": "v"},
        )
        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/projects",
            json={
                "name": "Full",
                "status": "active",
                "description": "Desc",
                "metadata": {"k": "v"},
            },
        )


class TestAsyncProjectUpdate:
    """Tests for AsyncProjectResource.update()."""

    @pytest.mark.asyncio()
    async def test_update_name(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request.return_value = {"name": "New"}
        await async_resource.update("p1", name="New")
        async_mock_client.request.assert_awaited_once_with(
            "PATCH", "/v1/projects/p1", json={"name": "New"}
        )

    @pytest.mark.asyncio()
    async def test_update_empty_payload(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request.return_value = {}
        await async_resource.update("p1")
        async_mock_client.request.assert_awaited_once_with(
            "PATCH", "/v1/projects/p1", json={}
        )


class TestAsyncProjectDelete:
    """Tests for AsyncProjectResource.delete()."""

    @pytest.mark.asyncio()
    async def test_delete(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request.return_value = None
        await async_resource.delete("p1")
        async_mock_client.request.assert_awaited_once_with(
            "DELETE", "/v1/projects/p1"
        )


class TestAsyncProjectMemoryLinks:
    """Tests for AsyncProjectResource memory link methods."""

    @pytest.mark.asyncio()
    async def test_add_memory_link(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        expected = {"id": "link_async"}
        async_mock_client.request.return_value = expected
        result = await async_resource.add_memory_link(
            "p1", "mem_1", "reference"
        )
        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/projects/p1/memory-links",
            json={
                "memoryItemId": "mem_1",
                "linkType": "reference",
            },
        )
        assert result == expected

    @pytest.mark.asyncio()
    async def test_remove_memory_link(
        self,
        async_mock_client: MagicMock,
        async_resource: AsyncProjectResource,
    ) -> None:
        async_mock_client.request.return_value = None
        await async_resource.remove_memory_link("p1", "link_1")
        async_mock_client.request.assert_awaited_once_with(
            "DELETE", "/v1/projects/p1/memory-links/link_1"
        )
