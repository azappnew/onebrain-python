from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class MemoryResource:
    """Sync resource for OneBrain Memory API (16 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list(
        self,
        *,
        type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List memory items with optional filtering and pagination.

        Args:
            type: Filter by memory type (fact, preference, decision,
                goal, experience, skill).
            status: Filter by status (active, candidate, archived,
                conflicted).
            search: Full-text search query.
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        if status is not None:
            params["status"] = status
        if search is not None:
            params["search"] = search
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return self._client.request_paginated("GET", "/v1/memory", params=params)

    def get(self, memory_id: str) -> Dict[str, Any]:
        """Retrieve a single memory item by ID.

        Args:
            memory_id: The memory item ID.

        Returns:
            The memory item object.
        """
        return self._client.request("GET", f"/v1/memory/{quote(memory_id, safe='')}")

    def create(
        self,
        type: str,
        title: str,
        body: str,
        *,
        source_type: Optional[str] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new memory item.

        Args:
            type: Memory type (fact, preference, decision, goal,
                experience, skill).
            title: Short descriptive title.
            body: Full content of the memory.
            source_type: Origin of the memory (user_input,
                system_inference, ai_extraction, user_confirmed).
            confidence: Confidence score between 0 and 1.
            metadata: Arbitrary key-value metadata.

        Returns:
            The created memory item.
        """
        payload: Dict[str, Any] = {
            "type": type,
            "title": title,
            "body": body,
        }
        if source_type is not None:
            payload["sourceType"] = source_type
        if confidence is not None:
            payload["confidence"] = confidence
        if metadata is not None:
            payload["metadata"] = metadata
        return self._client.request("POST", "/v1/memory", json=payload)

    def update(
        self,
        memory_id: str,
        *,
        title: Optional[str] = None,
        body: Optional[str] = None,
        confidence: Optional[float] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing memory item.

        Args:
            memory_id: The memory item ID.
            title: Updated title.
            body: Updated body content.
            confidence: Updated confidence score.
            status: Updated status (active, candidate, archived).
            metadata: Updated metadata.

        Returns:
            The updated memory item.
        """
        payload: Dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if confidence is not None:
            payload["confidence"] = confidence
        if status is not None:
            payload["status"] = status
        if metadata is not None:
            payload["metadata"] = metadata
        return self._client.request(
            "PATCH", f"/v1/memory/{quote(memory_id, safe='')}", json=payload
        )

    def delete(self, memory_id: str) -> None:
        """Delete a memory item.

        Args:
            memory_id: The memory item ID.
        """
        self._client.request(
            "DELETE", f"/v1/memory/{quote(memory_id, safe='')}"
        )

    def extract(
        self,
        type: str,
        title: str,
        body: str,
        *,
        source_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract and store a memory from provided content.

        Args:
            type: Memory type.
            title: Short descriptive title.
            body: Full content to extract from.
            source_type: Origin of the memory.

        Returns:
            The extracted memory item.
        """
        payload: Dict[str, Any] = {
            "type": type,
            "title": title,
            "body": body,
        }
        if source_type is not None:
            payload["sourceType"] = source_type
        return self._client.request("POST", "/v1/memory/extract", json=payload)

    def search(
        self,
        query: str,
        *,
        mode: Optional[str] = None,
        top_k: Optional[int] = None,
        alpha: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Deep search across memories using keyword, vector, or hybrid.

        Args:
            query: The search query string.
            mode: Search mode (keyword, vector, hybrid).
            top_k: Maximum number of results.
            alpha: Balance between keyword and vector (0.0-1.0).

        Returns:
            Search results with scores and search mode info.
        """
        payload: Dict[str, Any] = {"query": query}
        if mode is not None:
            payload["mode"] = mode
        if top_k is not None:
            payload["top_k"] = top_k
        if alpha is not None:
            payload["alpha"] = alpha
        return self._client.request("POST", "/v1/memory/search", json=payload)

    def consolidate(
        self,
        *,
        type: Optional[str] = None,
        threshold: Optional[float] = None,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Consolidate similar or overlapping memories.

        Args:
            type: Only consolidate memories of this type.
            threshold: Similarity threshold for merging.
            dry_run: If True, preview without applying changes.

        Returns:
            Consolidation result with affected items.
        """
        payload: Dict[str, Any] = {}
        if type is not None:
            payload["type"] = type
        if threshold is not None:
            payload["threshold"] = threshold
        if dry_run is not None:
            payload["dryRun"] = dry_run
        return self._client.request(
            "POST", "/v1/memory/consolidate", json=payload
        )

    def expire(
        self,
        *,
        ttl_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Expire old memories beyond the TTL threshold.

        Args:
            ttl_days: Number of days after which memories expire.

        Returns:
            Result with count of expired items.
        """
        payload: Dict[str, Any] = {}
        if ttl_days is not None:
            payload["ttlDays"] = ttl_days
        return self._client.request("POST", "/v1/memory/expire", json=payload)

    def duplicates(self) -> List[Dict[str, Any]]:
        """Detect duplicate memory groups.

        Returns:
            List of duplicate groups with similarity scores.
        """
        return self._client.request("GET", "/v1/memory/duplicates")

    def import_memories(
        self,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Bulk import memory items.

        Args:
            items: List of memory item dicts to import. Each must
                contain type, title, and body.

        Returns:
            Import result with counts.
        """
        return self._client.request(
            "POST", "/v1/memory/import", json={"items": items}
        )

    def ai_extract(
        self,
        text: str,
        *,
        ai_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract memories from text using AI.

        Args:
            text: Raw text to extract memories from.
            ai_provider: AI provider to use for extraction.

        Returns:
            Extraction result with discovered memories.
        """
        payload: Dict[str, Any] = {"text": text}
        if ai_provider is not None:
            payload["aiProvider"] = ai_provider
        return self._client.request(
            "POST", "/v1/memory/ai-extract", json=payload
        )

    def ingest_url(self, url: str) -> Dict[str, Any]:
        """Ingest content from a URL and create memories.

        Args:
            url: The URL to fetch and ingest.

        Returns:
            Ingestion result with created memories.
        """
        return self._client.request(
            "POST", "/v1/memory/ingest-url", json={"url": url}
        )

    def parse_chat(
        self,
        transcript: str,
        *,
        format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse a chat transcript and extract memories.

        Args:
            transcript: The chat transcript text.
            format: Transcript format hint.

        Returns:
            Parsing result with extracted memories.
        """
        payload: Dict[str, Any] = {"transcript": transcript}
        if format is not None:
            payload["format"] = format
        return self._client.request(
            "POST", "/v1/memory/parse-chat", json=payload
        )

    def embedding_status(self) -> Dict[str, Any]:
        """Get the status of memory embeddings.

        Returns:
            Embedding stats including total, embedded, pending,
            failed, missing, and coverage percentage.
        """
        return self._client.request("GET", "/v1/memory/embeddings/status")

    def reindex(
        self,
        *,
        status: Optional[str] = None,
        max_items: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Reindex memory embeddings.

        Args:
            status: Filter items to reindex (failed, missing).
            max_items: Maximum number of items to reindex.

        Returns:
            Reindex result with total, queued, and error counts.
        """
        payload: Dict[str, Any] = {}
        if status is not None:
            payload["status"] = status
        if max_items is not None:
            payload["maxItems"] = max_items
        return self._client.request(
            "POST", "/v1/memory/embeddings/reindex", json=payload
        )


class AsyncMemoryResource:
    """Async resource for OneBrain Memory API (16 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List memory items with optional filtering and pagination.

        Args:
            type: Filter by memory type (fact, preference, decision,
                goal, experience, skill).
            status: Filter by status (active, candidate, archived,
                conflicted).
            search: Full-text search query.
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        if status is not None:
            params["status"] = status
        if search is not None:
            params["search"] = search
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return await self._client.request_paginated(
            "GET", "/v1/memory", params=params
        )

    async def get(self, memory_id: str) -> Dict[str, Any]:
        """Retrieve a single memory item by ID.

        Args:
            memory_id: The memory item ID.

        Returns:
            The memory item object.
        """
        return await self._client.request(
            "GET", f"/v1/memory/{quote(memory_id, safe='')}"
        )

    async def create(
        self,
        type: str,
        title: str,
        body: str,
        *,
        source_type: Optional[str] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new memory item.

        Args:
            type: Memory type (fact, preference, decision, goal,
                experience, skill).
            title: Short descriptive title.
            body: Full content of the memory.
            source_type: Origin of the memory (user_input,
                system_inference, ai_extraction, user_confirmed).
            confidence: Confidence score between 0 and 1.
            metadata: Arbitrary key-value metadata.

        Returns:
            The created memory item.
        """
        payload: Dict[str, Any] = {
            "type": type,
            "title": title,
            "body": body,
        }
        if source_type is not None:
            payload["sourceType"] = source_type
        if confidence is not None:
            payload["confidence"] = confidence
        if metadata is not None:
            payload["metadata"] = metadata
        return await self._client.request("POST", "/v1/memory", json=payload)

    async def update(
        self,
        memory_id: str,
        *,
        title: Optional[str] = None,
        body: Optional[str] = None,
        confidence: Optional[float] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing memory item.

        Args:
            memory_id: The memory item ID.
            title: Updated title.
            body: Updated body content.
            confidence: Updated confidence score.
            status: Updated status (active, candidate, archived).
            metadata: Updated metadata.

        Returns:
            The updated memory item.
        """
        payload: Dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if confidence is not None:
            payload["confidence"] = confidence
        if status is not None:
            payload["status"] = status
        if metadata is not None:
            payload["metadata"] = metadata
        return await self._client.request(
            "PATCH", f"/v1/memory/{quote(memory_id, safe='')}", json=payload
        )

    async def delete(self, memory_id: str) -> None:
        """Delete a memory item.

        Args:
            memory_id: The memory item ID.
        """
        await self._client.request(
            "DELETE", f"/v1/memory/{quote(memory_id, safe='')}"
        )

    async def extract(
        self,
        type: str,
        title: str,
        body: str,
        *,
        source_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract and store a memory from provided content.

        Args:
            type: Memory type.
            title: Short descriptive title.
            body: Full content to extract from.
            source_type: Origin of the memory.

        Returns:
            The extracted memory item.
        """
        payload: Dict[str, Any] = {
            "type": type,
            "title": title,
            "body": body,
        }
        if source_type is not None:
            payload["sourceType"] = source_type
        return await self._client.request(
            "POST", "/v1/memory/extract", json=payload
        )

    async def search(
        self,
        query: str,
        *,
        mode: Optional[str] = None,
        top_k: Optional[int] = None,
        alpha: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Deep search across memories using keyword, vector, or hybrid.

        Args:
            query: The search query string.
            mode: Search mode (keyword, vector, hybrid).
            top_k: Maximum number of results.
            alpha: Balance between keyword and vector (0.0-1.0).

        Returns:
            Search results with scores and search mode info.
        """
        payload: Dict[str, Any] = {"query": query}
        if mode is not None:
            payload["mode"] = mode
        if top_k is not None:
            payload["top_k"] = top_k
        if alpha is not None:
            payload["alpha"] = alpha
        return await self._client.request(
            "POST", "/v1/memory/search", json=payload
        )

    async def consolidate(
        self,
        *,
        type: Optional[str] = None,
        threshold: Optional[float] = None,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Consolidate similar or overlapping memories.

        Args:
            type: Only consolidate memories of this type.
            threshold: Similarity threshold for merging.
            dry_run: If True, preview without applying changes.

        Returns:
            Consolidation result with affected items.
        """
        payload: Dict[str, Any] = {}
        if type is not None:
            payload["type"] = type
        if threshold is not None:
            payload["threshold"] = threshold
        if dry_run is not None:
            payload["dryRun"] = dry_run
        return await self._client.request(
            "POST", "/v1/memory/consolidate", json=payload
        )

    async def expire(
        self,
        *,
        ttl_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Expire old memories beyond the TTL threshold.

        Args:
            ttl_days: Number of days after which memories expire.

        Returns:
            Result with count of expired items.
        """
        payload: Dict[str, Any] = {}
        if ttl_days is not None:
            payload["ttlDays"] = ttl_days
        return await self._client.request(
            "POST", "/v1/memory/expire", json=payload
        )

    async def duplicates(self) -> List[Dict[str, Any]]:
        """Detect duplicate memory groups.

        Returns:
            List of duplicate groups with similarity scores.
        """
        return await self._client.request("GET", "/v1/memory/duplicates")

    async def import_memories(
        self,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Bulk import memory items.

        Args:
            items: List of memory item dicts to import. Each must
                contain type, title, and body.

        Returns:
            Import result with counts.
        """
        return await self._client.request(
            "POST", "/v1/memory/import", json={"items": items}
        )

    async def ai_extract(
        self,
        text: str,
        *,
        ai_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract memories from text using AI.

        Args:
            text: Raw text to extract memories from.
            ai_provider: AI provider to use for extraction.

        Returns:
            Extraction result with discovered memories.
        """
        payload: Dict[str, Any] = {"text": text}
        if ai_provider is not None:
            payload["aiProvider"] = ai_provider
        return await self._client.request(
            "POST", "/v1/memory/ai-extract", json=payload
        )

    async def ingest_url(self, url: str) -> Dict[str, Any]:
        """Ingest content from a URL and create memories.

        Args:
            url: The URL to fetch and ingest.

        Returns:
            Ingestion result with created memories.
        """
        return await self._client.request(
            "POST", "/v1/memory/ingest-url", json={"url": url}
        )

    async def parse_chat(
        self,
        transcript: str,
        *,
        format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse a chat transcript and extract memories.

        Args:
            transcript: The chat transcript text.
            format: Transcript format hint.

        Returns:
            Parsing result with extracted memories.
        """
        payload: Dict[str, Any] = {"transcript": transcript}
        if format is not None:
            payload["format"] = format
        return await self._client.request(
            "POST", "/v1/memory/parse-chat", json=payload
        )

    async def embedding_status(self) -> Dict[str, Any]:
        """Get the status of memory embeddings.

        Returns:
            Embedding stats including total, embedded, pending,
            failed, missing, and coverage percentage.
        """
        return await self._client.request(
            "GET", "/v1/memory/embeddings/status"
        )

    async def reindex(
        self,
        *,
        status: Optional[str] = None,
        max_items: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Reindex memory embeddings.

        Args:
            status: Filter items to reindex (failed, missing).
            max_items: Maximum number of items to reindex.

        Returns:
            Reindex result with total, queued, and error counts.
        """
        payload: Dict[str, Any] = {}
        if status is not None:
            payload["status"] = status
        if max_items is not None:
            payload["maxItems"] = max_items
        return await self._client.request(
            "POST", "/v1/memory/embeddings/reindex", json=payload
        )
