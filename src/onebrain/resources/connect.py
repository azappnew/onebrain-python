from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class ConnectResource:
    """Sync resource for OneBrain Connect API (4 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def read(
        self,
        *,
        scope: Optional[str] = None,
        format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Read connected context data.

        Args:
            scope: Context scope (brief, assistant, project, deep).
            format: Response format (text, json).

        Returns:
            Connected context data.
        """
        params: Dict[str, Any] = {}
        if scope is not None:
            params["scope"] = scope
        if format is not None:
            params["format"] = format
        return self._client.request("GET", "/v1/connect", params=params)

    def write_memory(
        self,
        type: str,
        title: str,
        body: str,
        *,
        source_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Write a single memory item via the Connect API.

        Args:
            type: Memory type (fact, preference, decision, goal,
                experience, skill).
            title: Short descriptive title.
            body: Full content of the memory.
            source_type: Origin of the memory (user_input,
                system_inference, ai_extraction, user_confirmed).

        Returns:
            Write result with status and item ID.
        """
        payload: Dict[str, Any] = {
            "type": type,
            "title": title,
            "body": body,
        }
        if source_type is not None:
            payload["sourceType"] = source_type
        return self._client.request(
            "POST", "/v1/connect/memory", json=payload
        )

    def write_memories(
        self,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Write multiple memory items in batch (up to 10).

        Args:
            items: List of memory item dicts. Each must contain
                type, title, and body.

        Returns:
            Batch result with per-item statuses, created count,
            and duplicates count.
        """
        return self._client.request(
            "POST", "/v1/connect/memories", json=items
        )

    def delta(self, since: str) -> Dict[str, Any]:
        """Retrieve changes since a given timestamp.

        Args:
            since: ISO 8601 timestamp to get changes from.

        Returns:
            Delta sync result with changes list and count.
        """
        return self._client.request(
            "GET", "/v1/connect/delta", params={"since": since}
        )


class AsyncConnectResource:
    """Async resource for OneBrain Connect API (4 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def read(
        self,
        *,
        scope: Optional[str] = None,
        format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Read connected context data.

        Args:
            scope: Context scope (brief, assistant, project, deep).
            format: Response format (text, json).

        Returns:
            Connected context data.
        """
        params: Dict[str, Any] = {}
        if scope is not None:
            params["scope"] = scope
        if format is not None:
            params["format"] = format
        return await self._client.request(
            "GET", "/v1/connect", params=params
        )

    async def write_memory(
        self,
        type: str,
        title: str,
        body: str,
        *,
        source_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Write a single memory item via the Connect API.

        Args:
            type: Memory type (fact, preference, decision, goal,
                experience, skill).
            title: Short descriptive title.
            body: Full content of the memory.
            source_type: Origin of the memory (user_input,
                system_inference, ai_extraction, user_confirmed).

        Returns:
            Write result with status and item ID.
        """
        payload: Dict[str, Any] = {
            "type": type,
            "title": title,
            "body": body,
        }
        if source_type is not None:
            payload["sourceType"] = source_type
        return await self._client.request(
            "POST", "/v1/connect/memory", json=payload
        )

    async def write_memories(
        self,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Write multiple memory items in batch (up to 10).

        Args:
            items: List of memory item dicts. Each must contain
                type, title, and body.

        Returns:
            Batch result with per-item statuses, created count,
            and duplicates count.
        """
        return await self._client.request(
            "POST", "/v1/connect/memories", json=items
        )

    async def delta(self, since: str) -> Dict[str, Any]:
        """Retrieve changes since a given timestamp.

        Args:
            since: ISO 8601 timestamp to get changes from.

        Returns:
            Delta sync result with changes list and count.
        """
        return await self._client.request(
            "GET", "/v1/connect/delta", params={"since": since}
        )
