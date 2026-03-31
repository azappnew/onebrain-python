"""Comprehensive tests for EntityResource and AsyncEntityResource."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.entity import AsyncEntityResource, EntityResource


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client():
    """Return a MagicMock that stands in for BaseClient."""
    return MagicMock()


@pytest.fixture
def entity(mock_client):
    """Return an EntityResource wired to the mocked client."""
    return EntityResource(mock_client)


@pytest.fixture
def async_mock_client():
    """Return an AsyncMock that stands in for AsyncBaseClient."""
    return AsyncMock()


@pytest.fixture
def async_entity(async_mock_client):
    """Return an AsyncEntityResource wired to the async mocked client."""
    return AsyncEntityResource(async_mock_client)


# ===================================================================
# Sync — EntityResource
# ===================================================================


class TestEntityList:
    """Tests for EntityResource.list()."""

    def test_list_default_params(self, mock_client, entity):
        expected = {
            "items": [],
            "cursor": None,
            "has_more": False,
            "total": 0,
        }
        mock_client.request_paginated.return_value = expected

        result = entity.list()

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/entities", params={},
        )
        assert result == expected

    def test_list_with_type_filter(self, mock_client, entity):
        mock_client.request_paginated.return_value = {"items": []}

        entity.list(type="person")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/entities", params={"type": "person"},
        )

    def test_list_with_cursor(self, mock_client, entity):
        mock_client.request_paginated.return_value = {"items": []}

        entity.list(cursor="cur_abc")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/entities", params={"cursor": "cur_abc"},
        )

    def test_list_with_limit(self, mock_client, entity):
        mock_client.request_paginated.return_value = {"items": []}

        entity.list(limit=50)

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/entities", params={"limit": 50},
        )

    def test_list_with_all_params(self, mock_client, entity):
        mock_client.request_paginated.return_value = {"items": []}

        entity.list(type="organization", cursor="xyz", limit=10)

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/entities",
            params={"type": "organization", "cursor": "xyz", "limit": 10},
        )

    def test_list_none_values_excluded(self, mock_client, entity):
        mock_client.request_paginated.return_value = {"items": []}

        entity.list(type=None, cursor=None, limit=None)

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/entities", params={},
        )


class TestEntityGet:
    """Tests for EntityResource.get()."""

    def test_get_by_id(self, mock_client, entity):
        expected = {"id": "ent_1", "name": "Alice", "type": "person"}
        mock_client.request.return_value = expected

        result = entity.get("ent_1")

        mock_client.request.assert_called_once_with(
            "GET", "/v1/entities/ent_1",
        )
        assert result == expected

    def test_get_url_encodes_special_chars(self, mock_client, entity):
        mock_client.request.return_value = {}

        entity.get("ent/special id")

        mock_client.request.assert_called_once_with(
            "GET", "/v1/entities/ent%2Fspecial%20id",
        )

    def test_get_uses_get_method(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.get("ent_1")
        assert mock_client.request.call_args[0][0] == "GET"


class TestEntityCreate:
    """Tests for EntityResource.create()."""

    def test_create_required_fields_only(self, mock_client, entity):
        expected = {"id": "ent_new", "name": "Bob", "type": "person"}
        mock_client.request.return_value = expected

        result = entity.create("Bob", "person")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities",
            json={"name": "Bob", "type": "person"},
        )
        assert result == expected

    def test_create_with_description(self, mock_client, entity):
        mock_client.request.return_value = {}

        entity.create("Acme Inc", "organization", description="A corp")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities",
            json={
                "name": "Acme Inc",
                "type": "organization",
                "description": "A corp",
            },
        )

    def test_create_with_metadata(self, mock_client, entity):
        meta = {"website": "https://acme.com"}
        mock_client.request.return_value = {}

        entity.create("Acme", "organization", metadata=meta)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities",
            json={
                "name": "Acme",
                "type": "organization",
                "metadata": meta,
            },
        )

    def test_create_with_all_optional_fields(self, mock_client, entity):
        meta = {"role": "engineer"}
        mock_client.request.return_value = {"id": "ent_x"}

        entity.create(
            "Charlie", "person",
            description="An engineer",
            metadata=meta,
        )

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities",
            json={
                "name": "Charlie",
                "type": "person",
                "description": "An engineer",
                "metadata": meta,
            },
        )

    def test_create_uses_post_method(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.create("N", "T")
        assert mock_client.request.call_args[0][0] == "POST"


class TestEntityUpdate:
    """Tests for EntityResource.update()."""

    def test_update_name(self, mock_client, entity):
        expected = {"id": "ent_1", "name": "Updated"}
        mock_client.request.return_value = expected

        result = entity.update("ent_1", name="Updated")

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/entities/ent_1",
            json={"name": "Updated"},
        )
        assert result == expected

    def test_update_type(self, mock_client, entity):
        mock_client.request.return_value = {}

        entity.update("ent_1", type="tool")

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/entities/ent_1",
            json={"type": "tool"},
        )

    def test_update_all_fields(self, mock_client, entity):
        meta = {"v": 2}
        mock_client.request.return_value = {}

        entity.update(
            "ent_1",
            name="New Name",
            type="concept",
            description="Updated desc",
            metadata=meta,
        )

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/entities/ent_1",
            json={
                "name": "New Name",
                "type": "concept",
                "description": "Updated desc",
                "metadata": meta,
            },
        )

    def test_update_empty_payload(self, mock_client, entity):
        mock_client.request.return_value = {}

        entity.update("ent_1")

        mock_client.request.assert_called_once_with(
            "PATCH", "/v1/entities/ent_1", json={},
        )

    def test_update_uses_patch(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.update("ent_1", name="X")
        assert mock_client.request.call_args[0][0] == "PATCH"

    def test_update_url_encodes_id(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.update("ent/1")
        mock_client.request.assert_called_once_with(
            "PATCH", "/v1/entities/ent%2F1", json={},
        )


class TestEntityDelete:
    """Tests for EntityResource.delete()."""

    def test_delete_by_id(self, mock_client, entity):
        mock_client.request.return_value = None

        result = entity.delete("ent_1")

        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/entities/ent_1",
        )
        assert result is None

    def test_delete_uses_delete_method(self, mock_client, entity):
        mock_client.request.return_value = None
        entity.delete("ent_1")
        assert mock_client.request.call_args[0][0] == "DELETE"

    def test_delete_url_encodes_id(self, mock_client, entity):
        mock_client.request.return_value = None
        entity.delete("ent/special")
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/entities/ent%2Fspecial",
        )


class TestEntityAddLink:
    """Tests for EntityResource.add_link()."""

    def test_add_link(self, mock_client, entity):
        expected = {
            "id": "lnk_1",
            "entity_id": "ent_1",
            "memory_item_id": "mem_1",
            "link_type": "mentions",
        }
        mock_client.request.return_value = expected

        result = entity.add_link("ent_1", "mem_1", "mentions")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities/ent_1/links",
            json={"memoryItemId": "mem_1", "linkType": "mentions"},
        )
        assert result == expected

    def test_add_link_uses_post(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.add_link("e", "m", "t")
        assert mock_client.request.call_args[0][0] == "POST"

    def test_add_link_url_encodes_entity_id(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.add_link("ent/1", "mem_1", "mentions")
        assert mock_client.request.call_args[0][1] == "/v1/entities/ent%2F1/links"


class TestEntityRemoveLink:
    """Tests for EntityResource.remove_link()."""

    def test_remove_link(self, mock_client, entity):
        mock_client.request.return_value = None

        result = entity.remove_link("ent_1", "lnk_1")

        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/entities/ent_1/links/lnk_1",
        )
        assert result is None

    def test_remove_link_uses_delete(self, mock_client, entity):
        mock_client.request.return_value = None
        entity.remove_link("e", "l")
        assert mock_client.request.call_args[0][0] == "DELETE"

    def test_remove_link_url_encodes_ids(self, mock_client, entity):
        mock_client.request.return_value = None
        entity.remove_link("ent/1", "lnk/2")
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/entities/ent%2F1/links/lnk%2F2",
        )


class TestEntityGraph:
    """Tests for EntityResource.graph()."""

    def test_graph(self, mock_client, entity):
        expected = {
            "nodes": [{"id": "ent_1", "name": "Alice"}],
            "edges": [{"source": "ent_1", "target": "ent_2"}],
        }
        mock_client.request.return_value = expected

        result = entity.graph()

        mock_client.request.assert_called_once_with(
            "GET", "/v1/entities/graph",
        )
        assert result == expected

    def test_graph_uses_get(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.graph()
        assert mock_client.request.call_args[0][0] == "GET"


class TestEntityDuplicates:
    """Tests for EntityResource.duplicates()."""

    def test_duplicates(self, mock_client, entity):
        expected = {"groups": [{"ids": ["e1", "e2"], "similarity": 0.95}]}
        mock_client.request.return_value = expected

        result = entity.duplicates()

        mock_client.request.assert_called_once_with(
            "GET", "/v1/entities/duplicates",
        )
        assert result == expected

    def test_duplicates_uses_get(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.duplicates()
        assert mock_client.request.call_args[0][0] == "GET"


class TestEntityMerge:
    """Tests for EntityResource.merge()."""

    def test_merge(self, mock_client, entity):
        expected = {"merged": True, "kept": "ent_1"}
        mock_client.request.return_value = expected

        result = entity.merge("ent_1", "ent_2")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities/merge",
            json={"keepId": "ent_1", "removeId": "ent_2"},
        )
        assert result == expected

    def test_merge_uses_post(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.merge("a", "b")
        assert mock_client.request.call_args[0][0] == "POST"

    def test_merge_path(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.merge("a", "b")
        assert mock_client.request.call_args[0][1] == "/v1/entities/merge"


class TestEntityAutoExtract:
    """Tests for EntityResource.auto_extract()."""

    def test_auto_extract(self, mock_client, entity):
        expected = {"entities": [{"name": "Python", "type": "tool"}]}
        mock_client.request.return_value = expected

        result = entity.auto_extract("mem_99")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities/auto-extract",
            json={"memoryId": "mem_99"},
        )
        assert result == expected

    def test_auto_extract_uses_post(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.auto_extract("m")
        assert mock_client.request.call_args[0][0] == "POST"

    def test_auto_extract_path(self, mock_client, entity):
        mock_client.request.return_value = {}
        entity.auto_extract("m")
        assert mock_client.request.call_args[0][1] == "/v1/entities/auto-extract"


# ===================================================================
# Async — AsyncEntityResource
# ===================================================================


class TestAsyncEntityList:
    """Tests for AsyncEntityResource.list()."""

    @pytest.mark.asyncio
    async def test_list_default(self, async_mock_client, async_entity):
        expected = {"items": [], "cursor": None, "has_more": False}
        async_mock_client.request_paginated.return_value = expected

        result = await async_entity.list()

        async_mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/entities", params={},
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_list_with_all_params(
        self, async_mock_client, async_entity,
    ):
        async_mock_client.request_paginated.return_value = {"items": []}

        await async_entity.list(type="tool", cursor="c", limit=25)

        async_mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/entities",
            params={"type": "tool", "cursor": "c", "limit": 25},
        )


class TestAsyncEntityGet:
    """Tests for AsyncEntityResource.get()."""

    @pytest.mark.asyncio
    async def test_get(self, async_mock_client, async_entity):
        expected = {"id": "ent_1", "name": "Alice"}
        async_mock_client.request.return_value = expected

        result = await async_entity.get("ent_1")

        async_mock_client.request.assert_called_once_with(
            "GET", "/v1/entities/ent_1",
        )
        assert result == expected


class TestAsyncEntityCreate:
    """Tests for AsyncEntityResource.create()."""

    @pytest.mark.asyncio
    async def test_create_required_only(
        self, async_mock_client, async_entity,
    ):
        async_mock_client.request.return_value = {"id": "ent_new"}

        result = await async_entity.create("Docker", "tool")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities",
            json={"name": "Docker", "type": "tool"},
        )
        assert result == {"id": "ent_new"}

    @pytest.mark.asyncio
    async def test_create_with_all_optionals(
        self, async_mock_client, async_entity,
    ):
        async_mock_client.request.return_value = {}

        await async_entity.create(
            "Kubernetes", "tool",
            description="Container orchestration",
            metadata={"category": "devops"},
        )

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities",
            json={
                "name": "Kubernetes",
                "type": "tool",
                "description": "Container orchestration",
                "metadata": {"category": "devops"},
            },
        )


class TestAsyncEntityUpdate:
    """Tests for AsyncEntityResource.update()."""

    @pytest.mark.asyncio
    async def test_update(self, async_mock_client, async_entity):
        async_mock_client.request.return_value = {"id": "ent_1"}

        result = await async_entity.update(
            "ent_1", name="Updated", description="New desc",
        )

        async_mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/entities/ent_1",
            json={"name": "Updated", "description": "New desc"},
        )
        assert result == {"id": "ent_1"}

    @pytest.mark.asyncio
    async def test_update_empty(self, async_mock_client, async_entity):
        async_mock_client.request.return_value = {}

        await async_entity.update("ent_1")

        async_mock_client.request.assert_called_once_with(
            "PATCH", "/v1/entities/ent_1", json={},
        )


class TestAsyncEntityDelete:
    """Tests for AsyncEntityResource.delete()."""

    @pytest.mark.asyncio
    async def test_delete(self, async_mock_client, async_entity):
        async_mock_client.request.return_value = None

        result = await async_entity.delete("ent_1")

        async_mock_client.request.assert_called_once_with(
            "DELETE", "/v1/entities/ent_1",
        )
        assert result is None


class TestAsyncEntityAddLink:
    """Tests for AsyncEntityResource.add_link()."""

    @pytest.mark.asyncio
    async def test_add_link(self, async_mock_client, async_entity):
        expected = {"id": "lnk_1"}
        async_mock_client.request.return_value = expected

        result = await async_entity.add_link("ent_1", "mem_1", "authored")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities/ent_1/links",
            json={"memoryItemId": "mem_1", "linkType": "authored"},
        )
        assert result == expected


class TestAsyncEntityRemoveLink:
    """Tests for AsyncEntityResource.remove_link()."""

    @pytest.mark.asyncio
    async def test_remove_link(self, async_mock_client, async_entity):
        async_mock_client.request.return_value = None

        result = await async_entity.remove_link("ent_1", "lnk_1")

        async_mock_client.request.assert_called_once_with(
            "DELETE", "/v1/entities/ent_1/links/lnk_1",
        )
        assert result is None


class TestAsyncEntityGraph:
    """Tests for AsyncEntityResource.graph()."""

    @pytest.mark.asyncio
    async def test_graph(self, async_mock_client, async_entity):
        expected = {"nodes": [], "edges": []}
        async_mock_client.request.return_value = expected

        result = await async_entity.graph()

        async_mock_client.request.assert_called_once_with(
            "GET", "/v1/entities/graph",
        )
        assert result == expected


class TestAsyncEntityDuplicates:
    """Tests for AsyncEntityResource.duplicates()."""

    @pytest.mark.asyncio
    async def test_duplicates(self, async_mock_client, async_entity):
        expected = {"groups": []}
        async_mock_client.request.return_value = expected

        result = await async_entity.duplicates()

        async_mock_client.request.assert_called_once_with(
            "GET", "/v1/entities/duplicates",
        )
        assert result == expected


class TestAsyncEntityMerge:
    """Tests for AsyncEntityResource.merge()."""

    @pytest.mark.asyncio
    async def test_merge(self, async_mock_client, async_entity):
        expected = {"merged": True}
        async_mock_client.request.return_value = expected

        result = await async_entity.merge("keep_1", "remove_2")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities/merge",
            json={"keepId": "keep_1", "removeId": "remove_2"},
        )
        assert result == expected


class TestAsyncEntityAutoExtract:
    """Tests for AsyncEntityResource.auto_extract()."""

    @pytest.mark.asyncio
    async def test_auto_extract(self, async_mock_client, async_entity):
        expected = {"entities": []}
        async_mock_client.request.return_value = expected

        result = await async_entity.auto_extract("mem_42")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/entities/auto-extract",
            json={"memoryId": "mem_42"},
        )
        assert result == expected


# ===================================================================
# Parametrized — HTTP method and path verification
# ===================================================================


@pytest.mark.parametrize(
    "method_name, expected_http, call_args",
    [
        ("get", "GET", ("ent_1",)),
        ("create", "POST", ("N", "T")),
        ("update", "PATCH", ("ent_1",)),
        ("delete", "DELETE", ("ent_1",)),
        ("add_link", "POST", ("ent_1", "mem_1", "mentions")),
        ("remove_link", "DELETE", ("ent_1", "lnk_1")),
        ("graph", "GET", ()),
        ("duplicates", "GET", ()),
        ("merge", "POST", ("k", "r")),
        ("auto_extract", "POST", ("mem_1",)),
    ],
    ids=[
        "get", "create", "update", "delete",
        "add_link", "remove_link", "graph",
        "duplicates", "merge", "auto_extract",
    ],
)
def test_sync_entity_methods_use_correct_http_verb(
    method_name, expected_http, call_args,
):
    mock_client = MagicMock()
    mock_client.request.return_value = {}
    mock_client.request_paginated.return_value = {"items": []}
    resource = EntityResource(mock_client)

    getattr(resource, method_name)(*call_args)

    if method_name == "list":
        actual = mock_client.request_paginated.call_args[0][0]
    else:
        actual = mock_client.request.call_args[0][0]
    assert actual == expected_http


@pytest.mark.parametrize(
    "method_name, expected_path, call_args",
    [
        ("get", "/v1/entities/ent_1", ("ent_1",)),
        ("create", "/v1/entities", ("N", "T")),
        ("update", "/v1/entities/ent_1", ("ent_1",)),
        ("delete", "/v1/entities/ent_1", ("ent_1",)),
        ("add_link", "/v1/entities/ent_1/links", ("ent_1", "m", "t")),
        (
            "remove_link",
            "/v1/entities/ent_1/links/lnk_1",
            ("ent_1", "lnk_1"),
        ),
        ("graph", "/v1/entities/graph", ()),
        ("duplicates", "/v1/entities/duplicates", ()),
        ("merge", "/v1/entities/merge", ("k", "r")),
        ("auto_extract", "/v1/entities/auto-extract", ("mem_1",)),
    ],
    ids=[
        "get", "create", "update", "delete",
        "add_link", "remove_link", "graph",
        "duplicates", "merge", "auto_extract",
    ],
)
def test_sync_entity_methods_use_correct_paths(
    method_name, expected_path, call_args,
):
    mock_client = MagicMock()
    mock_client.request.return_value = {}
    mock_client.request_paginated.return_value = {"items": []}
    resource = EntityResource(mock_client)

    getattr(resource, method_name)(*call_args)

    if method_name == "list":
        actual = mock_client.request_paginated.call_args[0][1]
    else:
        actual = mock_client.request.call_args[0][1]
    assert actual == expected_path


@pytest.mark.parametrize(
    "method_name, call_args, expected_json",
    [
        ("create", ("N", "T"), {"name": "N", "type": "T"}),
        (
            "add_link",
            ("ent_1", "mem_1", "mentions"),
            {"memoryItemId": "mem_1", "linkType": "mentions"},
        ),
        (
            "merge",
            ("keep_1", "remove_2"),
            {"keepId": "keep_1", "removeId": "remove_2"},
        ),
        (
            "auto_extract",
            ("mem_42",),
            {"memoryId": "mem_42"},
        ),
    ],
    ids=["create", "add_link", "merge", "auto_extract"],
)
def test_sync_entity_methods_send_correct_body(
    method_name, call_args, expected_json,
):
    mock_client = MagicMock()
    mock_client.request.return_value = {}
    resource = EntityResource(mock_client)

    getattr(resource, method_name)(*call_args)

    call_kwargs = mock_client.request.call_args[1]
    assert call_kwargs["json"] == expected_json
