from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class EntityResource:
    """Sync resource for OneBrain Entity API (11 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list(
        self,
        *,
        type: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List entities with optional filtering and pagination.

        Args:
            type: Filter by entity type.
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return self._client.request_paginated(
            "GET", "/v1/entities", params=params
        )

    def get(self, entity_id: str) -> Dict[str, Any]:
        """Retrieve a single entity by ID.

        Args:
            entity_id: The entity ID.

        Returns:
            The entity object.
        """
        return self._client.request(
            "GET", f"/v1/entities/{quote(entity_id, safe='')}"
        )

    def create(
        self,
        name: str,
        type: str,
        *,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new entity.

        Args:
            name: Entity name.
            type: Entity type (e.g., person, organization, tool).
            description: Optional description.
            metadata: Arbitrary key-value metadata.

        Returns:
            The created entity.
        """
        payload: Dict[str, Any] = {"name": name, "type": type}
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return self._client.request("POST", "/v1/entities", json=payload)

    def update(
        self,
        entity_id: str,
        *,
        name: Optional[str] = None,
        type: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing entity.

        Args:
            entity_id: The entity ID.
            name: Updated name.
            type: Updated type.
            description: Updated description.
            metadata: Updated metadata.

        Returns:
            The updated entity.
        """
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if type is not None:
            payload["type"] = type
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return self._client.request(
            "PATCH",
            f"/v1/entities/{quote(entity_id, safe='')}",
            json=payload,
        )

    def delete(self, entity_id: str) -> None:
        """Delete an entity.

        Args:
            entity_id: The entity ID.
        """
        self._client.request(
            "DELETE", f"/v1/entities/{quote(entity_id, safe='')}"
        )

    def add_link(
        self,
        entity_id: str,
        memory_item_id: str,
        link_type: str,
    ) -> Dict[str, Any]:
        """Link an entity to a memory item.

        Args:
            entity_id: The entity ID.
            memory_item_id: The memory item ID to link.
            link_type: Type of link relationship.

        Returns:
            The created entity link.
        """
        payload: Dict[str, Any] = {
            "memoryItemId": memory_item_id,
            "linkType": link_type,
        }
        return self._client.request(
            "POST",
            f"/v1/entities/{quote(entity_id, safe='')}/links",
            json=payload,
        )

    def remove_link(self, entity_id: str, link_id: str) -> None:
        """Remove a link between an entity and a memory item.

        Args:
            entity_id: The entity ID.
            link_id: The link ID to remove.
        """
        self._client.request(
            "DELETE",
            f"/v1/entities/{quote(entity_id, safe='')}"
            f"/links/{quote(link_id, safe='')}",
        )

    def graph(self) -> Dict[str, Any]:
        """Retrieve the full entity relationship graph.

        Returns:
            Graph data with nodes and edges.
        """
        return self._client.request("GET", "/v1/entities/graph")

    def duplicates(self) -> Dict[str, Any]:
        """Detect duplicate entities.

        Returns:
            Duplicate groups with similarity information.
        """
        return self._client.request("GET", "/v1/entities/duplicates")

    def merge(self, keep_id: str, remove_id: str) -> Dict[str, Any]:
        """Merge two entities, keeping one and removing the other.

        Args:
            keep_id: ID of the entity to keep.
            remove_id: ID of the entity to remove and merge into
                the kept entity.

        Returns:
            Merge result.
        """
        payload: Dict[str, Any] = {
            "keepId": keep_id,
            "removeId": remove_id,
        }
        return self._client.request(
            "POST", "/v1/entities/merge", json=payload
        )

    def auto_extract(self, memory_id: str) -> Dict[str, Any]:
        """Automatically extract entities from a memory item.

        Args:
            memory_id: The memory item ID to extract entities from.

        Returns:
            Extraction result with discovered entities.
        """
        return self._client.request(
            "POST",
            "/v1/entities/auto-extract",
            json={"memoryId": memory_id},
        )


class AsyncEntityResource:
    """Async resource for OneBrain Entity API (11 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        type: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List entities with optional filtering and pagination.

        Args:
            type: Filter by entity type.
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return await self._client.request_paginated(
            "GET", "/v1/entities", params=params
        )

    async def get(self, entity_id: str) -> Dict[str, Any]:
        """Retrieve a single entity by ID.

        Args:
            entity_id: The entity ID.

        Returns:
            The entity object.
        """
        return await self._client.request(
            "GET", f"/v1/entities/{quote(entity_id, safe='')}"
        )

    async def create(
        self,
        name: str,
        type: str,
        *,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new entity.

        Args:
            name: Entity name.
            type: Entity type (e.g., person, organization, tool).
            description: Optional description.
            metadata: Arbitrary key-value metadata.

        Returns:
            The created entity.
        """
        payload: Dict[str, Any] = {"name": name, "type": type}
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return await self._client.request(
            "POST", "/v1/entities", json=payload
        )

    async def update(
        self,
        entity_id: str,
        *,
        name: Optional[str] = None,
        type: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing entity.

        Args:
            entity_id: The entity ID.
            name: Updated name.
            type: Updated type.
            description: Updated description.
            metadata: Updated metadata.

        Returns:
            The updated entity.
        """
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if type is not None:
            payload["type"] = type
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return await self._client.request(
            "PATCH",
            f"/v1/entities/{quote(entity_id, safe='')}",
            json=payload,
        )

    async def delete(self, entity_id: str) -> None:
        """Delete an entity.

        Args:
            entity_id: The entity ID.
        """
        await self._client.request(
            "DELETE", f"/v1/entities/{quote(entity_id, safe='')}"
        )

    async def add_link(
        self,
        entity_id: str,
        memory_item_id: str,
        link_type: str,
    ) -> Dict[str, Any]:
        """Link an entity to a memory item.

        Args:
            entity_id: The entity ID.
            memory_item_id: The memory item ID to link.
            link_type: Type of link relationship.

        Returns:
            The created entity link.
        """
        payload: Dict[str, Any] = {
            "memoryItemId": memory_item_id,
            "linkType": link_type,
        }
        return await self._client.request(
            "POST",
            f"/v1/entities/{quote(entity_id, safe='')}/links",
            json=payload,
        )

    async def remove_link(self, entity_id: str, link_id: str) -> None:
        """Remove a link between an entity and a memory item.

        Args:
            entity_id: The entity ID.
            link_id: The link ID to remove.
        """
        await self._client.request(
            "DELETE",
            f"/v1/entities/{quote(entity_id, safe='')}"
            f"/links/{quote(link_id, safe='')}",
        )

    async def graph(self) -> Dict[str, Any]:
        """Retrieve the full entity relationship graph.

        Returns:
            Graph data with nodes and edges.
        """
        return await self._client.request("GET", "/v1/entities/graph")

    async def duplicates(self) -> Dict[str, Any]:
        """Detect duplicate entities.

        Returns:
            Duplicate groups with similarity information.
        """
        return await self._client.request("GET", "/v1/entities/duplicates")

    async def merge(self, keep_id: str, remove_id: str) -> Dict[str, Any]:
        """Merge two entities, keeping one and removing the other.

        Args:
            keep_id: ID of the entity to keep.
            remove_id: ID of the entity to remove and merge into
                the kept entity.

        Returns:
            Merge result.
        """
        payload: Dict[str, Any] = {
            "keepId": keep_id,
            "removeId": remove_id,
        }
        return await self._client.request(
            "POST", "/v1/entities/merge", json=payload
        )

    async def auto_extract(self, memory_id: str) -> Dict[str, Any]:
        """Automatically extract entities from a memory item.

        Args:
            memory_id: The memory item ID to extract entities from.

        Returns:
            Extraction result with discovered entities.
        """
        return await self._client.request(
            "POST",
            "/v1/entities/auto-extract",
            json={"memoryId": memory_id},
        )
