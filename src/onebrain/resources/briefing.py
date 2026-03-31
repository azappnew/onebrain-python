from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class BriefingResource:
    """Sync resource for OneBrain Briefing API (2 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def config(self) -> Dict[str, Any]:
        """Retrieve the briefing configuration.

        Returns:
            Briefing config with enabled flag, timezone,
            quiet hours, and active channels.
        """
        return self._client.request("GET", "/v1/briefings/config")

    def list(
        self,
        *,
        type: Optional[str] = None,
        status: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List briefings with optional filtering and pagination.

        Args:
            type: Filter by briefing type (morning, midday, evening,
                event_triggered, weekly_health).
            status: Filter by status (pending, generating, ready,
                delivered, failed).
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
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return self._client.request_paginated(
            "GET", "/v1/briefings", params=params
        )


class AsyncBriefingResource:
    """Async resource for OneBrain Briefing API (2 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def config(self) -> Dict[str, Any]:
        """Retrieve the briefing configuration.

        Returns:
            Briefing config with enabled flag, timezone,
            quiet hours, and active channels.
        """
        return await self._client.request("GET", "/v1/briefings/config")

    async def list(
        self,
        *,
        type: Optional[str] = None,
        status: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List briefings with optional filtering and pagination.

        Args:
            type: Filter by briefing type (morning, midday, evening,
                event_triggered, weekly_health).
            status: Filter by status (pending, generating, ready,
                delivered, failed).
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
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return await self._client.request_paginated(
            "GET", "/v1/briefings", params=params
        )
