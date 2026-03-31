"""Comprehensive tests for MemoryResource and AsyncMemoryResource."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.memory import AsyncMemoryResource, MemoryResource


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client():
    """Return a MagicMock that stands in for BaseClient."""
    return MagicMock()


@pytest.fixture
def memory(mock_client):
    """Return a MemoryResource wired to the mocked client."""
    return MemoryResource(mock_client)


@pytest.fixture
def async_mock_client():
    """Return an AsyncMock that stands in for AsyncBaseClient."""
    client = AsyncMock()
    return client


@pytest.fixture
def async_memory(async_mock_client):
    """Return an AsyncMemoryResource wired to the async mocked client."""
    return AsyncMemoryResource(async_mock_client)


# ===================================================================
# Sync — MemoryResource
# ===================================================================


class TestMemoryList:
    """Tests for MemoryResource.list()."""

    def test_list_default_params(self, mock_client, memory):
        expected = {
            "items": [],
            "cursor": None,
            "has_more": False,
            "total": 0,
        }
        mock_client.request_paginated.return_value = expected

        result = memory.list()

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/memory", params={},
        )
        assert result == expected

    def test_list_with_type_filter(self, mock_client, memory):
        mock_client.request_paginated.return_value = {"items": []}

        memory.list(type="fact")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/memory", params={"type": "fact"},
        )

    def test_list_with_status_filter(self, mock_client, memory):
        mock_client.request_paginated.return_value = {"items": []}

        memory.list(status="active")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/memory", params={"status": "active"},
        )

    def test_list_with_search_filter(self, mock_client, memory):
        mock_client.request_paginated.return_value = {"items": []}

        memory.list(search="python")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/memory", params={"search": "python"},
        )

    def test_list_with_pagination(self, mock_client, memory):
        mock_client.request_paginated.return_value = {"items": []}

        memory.list(cursor="abc123", limit=50)

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/memory",
            params={"cursor": "abc123", "limit": 50},
        )

    def test_list_with_all_filters(self, mock_client, memory):
        mock_client.request_paginated.return_value = {"items": []}

        memory.list(
            type="preference",
            status="archived",
            search="dark mode",
            cursor="xyz",
            limit=10,
        )

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/memory",
            params={
                "type": "preference",
                "status": "archived",
                "search": "dark mode",
                "cursor": "xyz",
                "limit": 10,
            },
        )

    def test_list_none_params_excluded(self, mock_client, memory):
        """None values must NOT appear in the params dict."""
        mock_client.request_paginated.return_value = {"items": []}

        memory.list(type=None, status=None)

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/memory", params={},
        )


class TestMemoryGet:
    """Tests for MemoryResource.get()."""

    def test_get_by_id(self, mock_client, memory):
        expected = {"id": "mem_1", "title": "Test"}
        mock_client.request.return_value = expected

        result = memory.get("mem_1")

        mock_client.request.assert_called_once_with(
            "GET", "/v1/memory/mem_1",
        )
        assert result == expected

    def test_get_url_encodes_special_chars(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.get("mem/special id")

        mock_client.request.assert_called_once_with(
            "GET", "/v1/memory/mem%2Fspecial%20id",
        )


class TestMemoryCreate:
    """Tests for MemoryResource.create()."""

    def test_create_required_fields_only(self, mock_client, memory):
        expected = {"id": "mem_new", "type": "fact", "title": "T", "body": "B"}
        mock_client.request.return_value = expected

        result = memory.create("fact", "T", "B")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory",
            json={"type": "fact", "title": "T", "body": "B"},
        )
        assert result == expected

    def test_create_with_all_optional_fields(self, mock_client, memory):
        meta = {"source": "chat"}
        mock_client.request.return_value = {"id": "mem_new"}

        memory.create(
            "preference",
            "Dark mode",
            "User prefers dark mode",
            source_type="user_input",
            confidence=0.95,
            metadata=meta,
        )

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory",
            json={
                "type": "preference",
                "title": "Dark mode",
                "body": "User prefers dark mode",
                "sourceType": "user_input",
                "confidence": 0.95,
                "metadata": meta,
            },
        )

    def test_create_with_source_type_only(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.create("goal", "Learn Rust", "Study Rust", source_type="ai_extraction")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory",
            json={
                "type": "goal",
                "title": "Learn Rust",
                "body": "Study Rust",
                "sourceType": "ai_extraction",
            },
        )

    def test_create_uses_post_method(self, mock_client, memory):
        mock_client.request.return_value = {}
        memory.create("fact", "t", "b")
        args = mock_client.request.call_args
        assert args[0][0] == "POST"


class TestMemoryUpdate:
    """Tests for MemoryResource.update()."""

    def test_update_title(self, mock_client, memory):
        expected = {"id": "mem_1", "title": "Updated"}
        mock_client.request.return_value = expected

        result = memory.update("mem_1", title="Updated")

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/memory/mem_1",
            json={"title": "Updated"},
        )
        assert result == expected

    def test_update_multiple_fields(self, mock_client, memory):
        mock_client.request.return_value = {}
        meta = {"version": 2}

        memory.update(
            "mem_1",
            title="New Title",
            body="New Body",
            confidence=0.8,
            status="archived",
            metadata=meta,
        )

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/memory/mem_1",
            json={
                "title": "New Title",
                "body": "New Body",
                "confidence": 0.8,
                "status": "archived",
                "metadata": meta,
            },
        )

    def test_update_empty_payload_when_no_fields(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.update("mem_1")

        mock_client.request.assert_called_once_with(
            "PATCH", "/v1/memory/mem_1", json={},
        )

    def test_update_uses_patch_method(self, mock_client, memory):
        mock_client.request.return_value = {}
        memory.update("mem_1", body="x")
        args = mock_client.request.call_args
        assert args[0][0] == "PATCH"

    def test_update_url_encodes_id(self, mock_client, memory):
        mock_client.request.return_value = {}
        memory.update("mem/1")
        mock_client.request.assert_called_once_with(
            "PATCH", "/v1/memory/mem%2F1", json={},
        )


class TestMemoryDelete:
    """Tests for MemoryResource.delete()."""

    def test_delete_by_id(self, mock_client, memory):
        mock_client.request.return_value = None

        result = memory.delete("mem_1")

        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/memory/mem_1",
        )
        assert result is None

    def test_delete_uses_delete_method(self, mock_client, memory):
        mock_client.request.return_value = None
        memory.delete("mem_1")
        args = mock_client.request.call_args
        assert args[0][0] == "DELETE"


class TestMemoryExtract:
    """Tests for MemoryResource.extract()."""

    def test_extract_required_fields(self, mock_client, memory):
        expected = {"id": "mem_ext_1", "type": "fact"}
        mock_client.request.return_value = expected

        result = memory.extract("fact", "Title", "Body content")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/extract",
            json={"type": "fact", "title": "Title", "body": "Body content"},
        )
        assert result == expected

    def test_extract_with_source_type(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.extract(
            "decision", "Architecture", "Use microservices",
            source_type="system_inference",
        )

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/extract",
            json={
                "type": "decision",
                "title": "Architecture",
                "body": "Use microservices",
                "sourceType": "system_inference",
            },
        )


class TestMemorySearch:
    """Tests for MemoryResource.search()."""

    def test_search_query_only(self, mock_client, memory):
        expected = {"results": [], "search_mode": "hybrid"}
        mock_client.request.return_value = expected

        result = memory.search("python programming")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/search",
            json={"query": "python programming"},
        )
        assert result == expected

    def test_search_with_mode(self, mock_client, memory):
        mock_client.request.return_value = {"results": []}

        memory.search("rust", mode="keyword")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/search",
            json={"query": "rust", "mode": "keyword"},
        )

    def test_search_with_top_k(self, mock_client, memory):
        mock_client.request.return_value = {"results": []}

        memory.search("test", top_k=5)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/search",
            json={"query": "test", "top_k": 5},
        )

    def test_search_with_alpha(self, mock_client, memory):
        mock_client.request.return_value = {"results": []}

        memory.search("test", alpha=0.7)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/search",
            json={"query": "test", "alpha": 0.7},
        )

    def test_search_with_all_options(self, mock_client, memory):
        mock_client.request.return_value = {"results": []}

        memory.search("query", mode="vector", top_k=10, alpha=0.5)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/search",
            json={
                "query": "query",
                "mode": "vector",
                "top_k": 10,
                "alpha": 0.5,
            },
        )

    def test_search_uses_post_method(self, mock_client, memory):
        mock_client.request.return_value = {}
        memory.search("q")
        assert mock_client.request.call_args[0][0] == "POST"


class TestMemoryConsolidate:
    """Tests for MemoryResource.consolidate()."""

    def test_consolidate_default(self, mock_client, memory):
        expected = {"merged": 3}
        mock_client.request.return_value = expected

        result = memory.consolidate()

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/consolidate", json={},
        )
        assert result == expected

    def test_consolidate_with_type(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.consolidate(type="fact")

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/consolidate", json={"type": "fact"},
        )

    def test_consolidate_with_threshold(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.consolidate(threshold=0.85)

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/consolidate", json={"threshold": 0.85},
        )

    def test_consolidate_dry_run(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.consolidate(dry_run=True)

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/consolidate", json={"dryRun": True},
        )

    def test_consolidate_all_options(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.consolidate(type="preference", threshold=0.9, dry_run=False)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/consolidate",
            json={
                "type": "preference",
                "threshold": 0.9,
                "dryRun": False,
            },
        )


class TestMemoryExpire:
    """Tests for MemoryResource.expire()."""

    def test_expire_default(self, mock_client, memory):
        expected = {"expired": 5}
        mock_client.request.return_value = expected

        result = memory.expire()

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/expire", json={},
        )
        assert result == expected

    def test_expire_with_ttl(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.expire(ttl_days=30)

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/expire", json={"ttlDays": 30},
        )


class TestMemoryDuplicates:
    """Tests for MemoryResource.duplicates()."""

    def test_duplicates(self, mock_client, memory):
        expected = [
            {"id": "grp_1", "title": "Group", "duplicates": []},
        ]
        mock_client.request.return_value = expected

        result = memory.duplicates()

        mock_client.request.assert_called_once_with(
            "GET", "/v1/memory/duplicates",
        )
        assert result == expected

    def test_duplicates_uses_get(self, mock_client, memory):
        mock_client.request.return_value = []
        memory.duplicates()
        assert mock_client.request.call_args[0][0] == "GET"


class TestMemoryImport:
    """Tests for MemoryResource.import_memories()."""

    def test_import_memories(self, mock_client, memory):
        items = [
            {"type": "fact", "title": "A", "body": "a"},
            {"type": "goal", "title": "B", "body": "b"},
        ]
        expected = {"created": 2, "duplicates": 0}
        mock_client.request.return_value = expected

        result = memory.import_memories(items)

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/import", json={"items": items},
        )
        assert result == expected

    def test_import_empty_list(self, mock_client, memory):
        mock_client.request.return_value = {"created": 0}

        memory.import_memories([])

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/import", json={"items": []},
        )


class TestMemoryAiExtract:
    """Tests for MemoryResource.ai_extract()."""

    def test_ai_extract_text_only(self, mock_client, memory):
        expected = {"memories": [{"title": "Extracted"}]}
        mock_client.request.return_value = expected

        result = memory.ai_extract("Some long text to analyze")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/ai-extract",
            json={"text": "Some long text to analyze"},
        )
        assert result == expected

    def test_ai_extract_with_provider(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.ai_extract("text", ai_provider="openai")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/ai-extract",
            json={"text": "text", "aiProvider": "openai"},
        )


class TestMemoryIngestUrl:
    """Tests for MemoryResource.ingest_url()."""

    def test_ingest_url(self, mock_client, memory):
        expected = {"memories": [{"title": "From URL"}]}
        mock_client.request.return_value = expected

        result = memory.ingest_url("https://example.com/article")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/ingest-url",
            json={"url": "https://example.com/article"},
        )
        assert result == expected


class TestMemoryParseChat:
    """Tests for MemoryResource.parse_chat()."""

    def test_parse_chat_transcript_only(self, mock_client, memory):
        transcript = "User: Hello\nAssistant: Hi"
        expected = {"memories": []}
        mock_client.request.return_value = expected

        result = memory.parse_chat(transcript)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/parse-chat",
            json={"transcript": transcript},
        )
        assert result == expected

    def test_parse_chat_with_format(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.parse_chat("transcript text", format="slack")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/parse-chat",
            json={"transcript": "transcript text", "format": "slack"},
        )


class TestMemoryEmbeddingStatus:
    """Tests for MemoryResource.embedding_status()."""

    def test_embedding_status(self, mock_client, memory):
        expected = {
            "total_memories": 100,
            "embedded": 95,
            "pending": 3,
            "failed": 1,
            "missing": 1,
            "coverage": 0.95,
        }
        mock_client.request.return_value = expected

        result = memory.embedding_status()

        mock_client.request.assert_called_once_with(
            "GET", "/v1/memory/embeddings/status",
        )
        assert result == expected

    def test_embedding_status_uses_get(self, mock_client, memory):
        mock_client.request.return_value = {}
        memory.embedding_status()
        assert mock_client.request.call_args[0][0] == "GET"


class TestMemoryReindex:
    """Tests for MemoryResource.reindex()."""

    def test_reindex_default(self, mock_client, memory):
        expected = {"total": 10, "queued": 10, "errors": 0}
        mock_client.request.return_value = expected

        result = memory.reindex()

        mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/embeddings/reindex", json={},
        )
        assert result == expected

    def test_reindex_with_status(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.reindex(status="failed")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/embeddings/reindex",
            json={"status": "failed"},
        )

    def test_reindex_with_max_items(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.reindex(max_items=50)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/embeddings/reindex",
            json={"maxItems": 50},
        )

    def test_reindex_with_all_options(self, mock_client, memory):
        mock_client.request.return_value = {}

        memory.reindex(status="missing", max_items=25)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/embeddings/reindex",
            json={"status": "missing", "maxItems": 25},
        )


# ===================================================================
# Async — AsyncMemoryResource
# ===================================================================


class TestAsyncMemoryList:
    """Tests for AsyncMemoryResource.list()."""

    @pytest.mark.asyncio
    async def test_list_default(self, async_mock_client, async_memory):
        expected = {"items": [], "cursor": None, "has_more": False}
        async_mock_client.request_paginated.return_value = expected

        result = await async_memory.list()

        async_mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/memory", params={},
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_list_with_filters(self, async_mock_client, async_memory):
        async_mock_client.request_paginated.return_value = {"items": []}

        await async_memory.list(
            type="skill", status="candidate", search="q", cursor="c", limit=5,
        )

        async_mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/memory",
            params={
                "type": "skill",
                "status": "candidate",
                "search": "q",
                "cursor": "c",
                "limit": 5,
            },
        )


class TestAsyncMemoryGet:
    """Tests for AsyncMemoryResource.get()."""

    @pytest.mark.asyncio
    async def test_get(self, async_mock_client, async_memory):
        expected = {"id": "mem_1"}
        async_mock_client.request.return_value = expected

        result = await async_memory.get("mem_1")

        async_mock_client.request.assert_called_once_with(
            "GET", "/v1/memory/mem_1",
        )
        assert result == expected


class TestAsyncMemoryCreate:
    """Tests for AsyncMemoryResource.create()."""

    @pytest.mark.asyncio
    async def test_create_required_only(
        self, async_mock_client, async_memory,
    ):
        async_mock_client.request.return_value = {"id": "new"}

        result = await async_memory.create("fact", "Title", "Body")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory",
            json={"type": "fact", "title": "Title", "body": "Body"},
        )
        assert result == {"id": "new"}

    @pytest.mark.asyncio
    async def test_create_with_optionals(
        self, async_mock_client, async_memory,
    ):
        async_mock_client.request.return_value = {}

        await async_memory.create(
            "decision", "D", "B",
            source_type="user_confirmed",
            confidence=0.7,
            metadata={"k": "v"},
        )

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory",
            json={
                "type": "decision",
                "title": "D",
                "body": "B",
                "sourceType": "user_confirmed",
                "confidence": 0.7,
                "metadata": {"k": "v"},
            },
        )


class TestAsyncMemoryUpdate:
    """Tests for AsyncMemoryResource.update()."""

    @pytest.mark.asyncio
    async def test_update(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"id": "mem_1"}

        result = await async_memory.update("mem_1", title="New")

        async_mock_client.request.assert_called_once_with(
            "PATCH", "/v1/memory/mem_1", json={"title": "New"},
        )
        assert result == {"id": "mem_1"}


class TestAsyncMemoryDelete:
    """Tests for AsyncMemoryResource.delete()."""

    @pytest.mark.asyncio
    async def test_delete(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = None

        result = await async_memory.delete("mem_1")

        async_mock_client.request.assert_called_once_with(
            "DELETE", "/v1/memory/mem_1",
        )
        assert result is None


class TestAsyncMemoryExtract:
    """Tests for AsyncMemoryResource.extract()."""

    @pytest.mark.asyncio
    async def test_extract(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"id": "ext_1"}

        result = await async_memory.extract("fact", "T", "B")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/extract",
            json={"type": "fact", "title": "T", "body": "B"},
        )
        assert result == {"id": "ext_1"}

    @pytest.mark.asyncio
    async def test_extract_with_source_type(
        self, async_mock_client, async_memory,
    ):
        async_mock_client.request.return_value = {}

        await async_memory.extract(
            "skill", "T", "B", source_type="ai_extraction",
        )

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/extract",
            json={
                "type": "skill",
                "title": "T",
                "body": "B",
                "sourceType": "ai_extraction",
            },
        )


class TestAsyncMemorySearch:
    """Tests for AsyncMemoryResource.search()."""

    @pytest.mark.asyncio
    async def test_search(self, async_mock_client, async_memory):
        expected = {"results": [{"id": "m1", "score": 0.9}]}
        async_mock_client.request.return_value = expected

        result = await async_memory.search("query")

        async_mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/search", json={"query": "query"},
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_search_with_all_options(
        self, async_mock_client, async_memory,
    ):
        async_mock_client.request.return_value = {"results": []}

        await async_memory.search(
            "q", mode="hybrid", top_k=3, alpha=0.6,
        )

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/search",
            json={
                "query": "q",
                "mode": "hybrid",
                "top_k": 3,
                "alpha": 0.6,
            },
        )


class TestAsyncMemoryConsolidate:
    """Tests for AsyncMemoryResource.consolidate()."""

    @pytest.mark.asyncio
    async def test_consolidate(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"merged": 2}

        result = await async_memory.consolidate(
            type="fact", threshold=0.8, dry_run=True,
        )

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/consolidate",
            json={"type": "fact", "threshold": 0.8, "dryRun": True},
        )
        assert result == {"merged": 2}


class TestAsyncMemoryExpire:
    """Tests for AsyncMemoryResource.expire()."""

    @pytest.mark.asyncio
    async def test_expire(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"expired": 1}

        result = await async_memory.expire(ttl_days=7)

        async_mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/expire", json={"ttlDays": 7},
        )
        assert result == {"expired": 1}


class TestAsyncMemoryDuplicates:
    """Tests for AsyncMemoryResource.duplicates()."""

    @pytest.mark.asyncio
    async def test_duplicates(self, async_mock_client, async_memory):
        expected = [{"id": "g1", "duplicates": []}]
        async_mock_client.request.return_value = expected

        result = await async_memory.duplicates()

        async_mock_client.request.assert_called_once_with(
            "GET", "/v1/memory/duplicates",
        )
        assert result == expected


class TestAsyncMemoryImport:
    """Tests for AsyncMemoryResource.import_memories()."""

    @pytest.mark.asyncio
    async def test_import(self, async_mock_client, async_memory):
        items = [{"type": "fact", "title": "X", "body": "Y"}]
        async_mock_client.request.return_value = {"created": 1}

        result = await async_memory.import_memories(items)

        async_mock_client.request.assert_called_once_with(
            "POST", "/v1/memory/import", json={"items": items},
        )
        assert result == {"created": 1}


class TestAsyncMemoryAiExtract:
    """Tests for AsyncMemoryResource.ai_extract()."""

    @pytest.mark.asyncio
    async def test_ai_extract(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"memories": []}

        result = await async_memory.ai_extract("raw text", ai_provider="gemini")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/ai-extract",
            json={"text": "raw text", "aiProvider": "gemini"},
        )
        assert result == {"memories": []}


class TestAsyncMemoryIngestUrl:
    """Tests for AsyncMemoryResource.ingest_url()."""

    @pytest.mark.asyncio
    async def test_ingest_url(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"memories": []}

        result = await async_memory.ingest_url("https://example.com")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/ingest-url",
            json={"url": "https://example.com"},
        )
        assert result == {"memories": []}


class TestAsyncMemoryParseChat:
    """Tests for AsyncMemoryResource.parse_chat()."""

    @pytest.mark.asyncio
    async def test_parse_chat(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"memories": []}

        result = await async_memory.parse_chat("chat log", format="discord")

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/parse-chat",
            json={"transcript": "chat log", "format": "discord"},
        )
        assert result == {"memories": []}


class TestAsyncMemoryEmbeddingStatus:
    """Tests for AsyncMemoryResource.embedding_status()."""

    @pytest.mark.asyncio
    async def test_embedding_status(self, async_mock_client, async_memory):
        expected = {"total_memories": 50, "coverage": 0.9}
        async_mock_client.request.return_value = expected

        result = await async_memory.embedding_status()

        async_mock_client.request.assert_called_once_with(
            "GET", "/v1/memory/embeddings/status",
        )
        assert result == expected


class TestAsyncMemoryReindex:
    """Tests for AsyncMemoryResource.reindex()."""

    @pytest.mark.asyncio
    async def test_reindex(self, async_mock_client, async_memory):
        async_mock_client.request.return_value = {"queued": 5}

        result = await async_memory.reindex(status="failed", max_items=10)

        async_mock_client.request.assert_called_once_with(
            "POST",
            "/v1/memory/embeddings/reindex",
            json={"status": "failed", "maxItems": 10},
        )
        assert result == {"queued": 5}


# ===================================================================
# Parametrized — HTTP method verification
# ===================================================================


@pytest.mark.parametrize(
    "method_name, expected_http, call_args, call_kwargs",
    [
        ("get", "GET", ("mem_1",), {}),
        ("create", "POST", ("fact", "T", "B"), {}),
        ("delete", "DELETE", ("mem_1",), {}),
        ("extract", "POST", ("fact", "T", "B"), {}),
        ("search", "POST", ("q",), {}),
        ("consolidate", "POST", (), {}),
        ("expire", "POST", (), {}),
        ("duplicates", "GET", (), {}),
        ("import_memories", "POST", ([],), {}),
        ("ai_extract", "POST", ("text",), {}),
        ("ingest_url", "POST", ("https://u.rl",), {}),
        ("parse_chat", "POST", ("transcript",), {}),
        ("embedding_status", "GET", (), {}),
        ("reindex", "POST", (), {}),
    ],
    ids=lambda val: val if isinstance(val, str) else "",
)
def test_sync_methods_use_correct_http_verb(
    method_name, expected_http, call_args, call_kwargs,
):
    mock_client = MagicMock()
    mock_client.request.return_value = {}
    mock_client.request_paginated.return_value = {"items": []}
    resource = MemoryResource(mock_client)

    getattr(resource, method_name)(*call_args, **call_kwargs)

    if method_name == "list":
        actual_method = mock_client.request_paginated.call_args[0][0]
    else:
        actual_method = mock_client.request.call_args[0][0]
    assert actual_method == expected_http


@pytest.mark.parametrize(
    "method_name, expected_path, call_args",
    [
        ("get", "/v1/memory/test_id", ("test_id",)),
        ("create", "/v1/memory", ("fact", "T", "B")),
        ("update", "/v1/memory/test_id", ("test_id",)),
        ("delete", "/v1/memory/test_id", ("test_id",)),
        ("extract", "/v1/memory/extract", ("fact", "T", "B")),
        ("search", "/v1/memory/search", ("q",)),
        ("consolidate", "/v1/memory/consolidate", ()),
        ("expire", "/v1/memory/expire", ()),
        ("duplicates", "/v1/memory/duplicates", ()),
        ("import_memories", "/v1/memory/import", ([],)),
        ("ai_extract", "/v1/memory/ai-extract", ("text",)),
        ("ingest_url", "/v1/memory/ingest-url", ("https://x.com",)),
        ("parse_chat", "/v1/memory/parse-chat", ("t",)),
        ("embedding_status", "/v1/memory/embeddings/status", ()),
        ("reindex", "/v1/memory/embeddings/reindex", ()),
    ],
    ids=lambda val: val if isinstance(val, str) else "",
)
def test_sync_methods_use_correct_paths(
    method_name, expected_path, call_args,
):
    mock_client = MagicMock()
    mock_client.request.return_value = {}
    mock_client.request_paginated.return_value = {"items": []}
    resource = MemoryResource(mock_client)

    getattr(resource, method_name)(*call_args)

    if method_name == "list":
        actual_path = mock_client.request_paginated.call_args[0][1]
    else:
        actual_path = mock_client.request.call_args[0][1]
    assert actual_path == expected_path
