from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import quote

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class ProjectResource:
    """Sync resource for OneBrain Project API (7 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list(
        self,
        *,
        status: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List projects with optional filtering and pagination.

        Args:
            status: Filter by project status (active, archived,
                completed).
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return self._client.request_paginated(
            "GET", "/v1/projects", params=params
        )

    def get(self, project_id: str) -> Dict[str, Any]:
        """Retrieve a single project by ID.

        Args:
            project_id: The project ID.

        Returns:
            The project object.
        """
        return self._client.request(
            "GET", f"/v1/projects/{quote(project_id, safe='')}"
        )

    def create(
        self,
        name: str,
        *,
        status: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new project.

        Args:
            name: Project name.
            status: Initial status (active, archived, completed).
            description: Optional description.
            metadata: Arbitrary key-value metadata.

        Returns:
            The created project.
        """
        payload: Dict[str, Any] = {"name": name}
        if status is not None:
            payload["status"] = status
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return self._client.request("POST", "/v1/projects", json=payload)

    def update(
        self,
        project_id: str,
        *,
        name: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing project.

        Args:
            project_id: The project ID.
            name: Updated name.
            status: Updated status (active, archived, completed).
            description: Updated description.
            metadata: Updated metadata.

        Returns:
            The updated project.
        """
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if status is not None:
            payload["status"] = status
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return self._client.request(
            "PATCH",
            f"/v1/projects/{quote(project_id, safe='')}",
            json=payload,
        )

    def delete(self, project_id: str) -> None:
        """Delete a project.

        Args:
            project_id: The project ID.
        """
        self._client.request(
            "DELETE", f"/v1/projects/{quote(project_id, safe='')}"
        )

    def add_memory_link(
        self,
        project_id: str,
        memory_item_id: str,
        link_type: str,
    ) -> Dict[str, Any]:
        """Link a memory item to a project.

        Args:
            project_id: The project ID.
            memory_item_id: The memory item ID to link.
            link_type: Type of link relationship.

        Returns:
            The created project-memory link.
        """
        payload: Dict[str, Any] = {
            "memoryItemId": memory_item_id,
            "linkType": link_type,
        }
        return self._client.request(
            "POST",
            f"/v1/projects/{quote(project_id, safe='')}/memory-links",
            json=payload,
        )

    def remove_memory_link(
        self,
        project_id: str,
        link_id: str,
    ) -> None:
        """Remove a memory link from a project.

        Args:
            project_id: The project ID.
            link_id: The link ID to remove.
        """
        self._client.request(
            "DELETE",
            f"/v1/projects/{quote(project_id, safe='')}"
            f"/memory-links/{quote(link_id, safe='')}",
        )


class AsyncProjectResource:
    """Async resource for OneBrain Project API (7 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        status: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List projects with optional filtering and pagination.

        Args:
            status: Filter by project status (active, archived,
                completed).
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return await self._client.request_paginated(
            "GET", "/v1/projects", params=params
        )

    async def get(self, project_id: str) -> Dict[str, Any]:
        """Retrieve a single project by ID.

        Args:
            project_id: The project ID.

        Returns:
            The project object.
        """
        return await self._client.request(
            "GET", f"/v1/projects/{quote(project_id, safe='')}"
        )

    async def create(
        self,
        name: str,
        *,
        status: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new project.

        Args:
            name: Project name.
            status: Initial status (active, archived, completed).
            description: Optional description.
            metadata: Arbitrary key-value metadata.

        Returns:
            The created project.
        """
        payload: Dict[str, Any] = {"name": name}
        if status is not None:
            payload["status"] = status
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return await self._client.request(
            "POST", "/v1/projects", json=payload
        )

    async def update(
        self,
        project_id: str,
        *,
        name: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing project.

        Args:
            project_id: The project ID.
            name: Updated name.
            status: Updated status (active, archived, completed).
            description: Updated description.
            metadata: Updated metadata.

        Returns:
            The updated project.
        """
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if status is not None:
            payload["status"] = status
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return await self._client.request(
            "PATCH",
            f"/v1/projects/{quote(project_id, safe='')}",
            json=payload,
        )

    async def delete(self, project_id: str) -> None:
        """Delete a project.

        Args:
            project_id: The project ID.
        """
        await self._client.request(
            "DELETE", f"/v1/projects/{quote(project_id, safe='')}"
        )

    async def add_memory_link(
        self,
        project_id: str,
        memory_item_id: str,
        link_type: str,
    ) -> Dict[str, Any]:
        """Link a memory item to a project.

        Args:
            project_id: The project ID.
            memory_item_id: The memory item ID to link.
            link_type: Type of link relationship.

        Returns:
            The created project-memory link.
        """
        payload: Dict[str, Any] = {
            "memoryItemId": memory_item_id,
            "linkType": link_type,
        }
        return await self._client.request(
            "POST",
            f"/v1/projects/{quote(project_id, safe='')}/memory-links",
            json=payload,
        )

    async def remove_memory_link(
        self,
        project_id: str,
        link_id: str,
    ) -> None:
        """Remove a memory link from a project.

        Args:
            project_id: The project ID.
            link_id: The link ID to remove.
        """
        await self._client.request(
            "DELETE",
            f"/v1/projects/{quote(project_id, safe='')}"
            f"/memory-links/{quote(link_id, safe='')}",
        )
