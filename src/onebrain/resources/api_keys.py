from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class ApiKeysResource:
    """Sync resource for OneBrain API Keys API (4 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list(
        self,
        *,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List API keys with pagination.

        Args:
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return self._client.request_paginated(
            "GET", "/v1/api-keys", params=params
        )

    def create(
        self,
        name: str,
        *,
        scopes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new API key.

        Args:
            name: Human-readable name for the key.
            scopes: Optional list of permission scopes.

        Returns:
            The created API key including the full key value
            (only returned once at creation time).
        """
        payload: Dict[str, Any] = {"name": name}
        if scopes is not None:
            payload["scopes"] = scopes
        return self._client.request("POST", "/v1/api-keys", json=payload)

    def update_trust_level(
        self,
        key_id: str,
        level: str,
    ) -> Dict[str, Any]:
        """Update the trust level of an API key.

        Args:
            key_id: The API key ID.
            level: New trust level (review, trusted).

        Returns:
            The updated API key.
        """
        return self._client.request(
            "PATCH",
            f"/v1/api-keys/{quote(key_id, safe='')}/trust",
            json={"trustLevel": level},
        )

    def revoke(self, key_id: str) -> None:
        """Revoke (delete) an API key.

        Args:
            key_id: The API key ID to revoke.
        """
        self._client.request(
            "DELETE", f"/v1/api-keys/{quote(key_id, safe='')}"
        )


class AsyncApiKeysResource:
    """Async resource for OneBrain API Keys API (4 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List API keys with pagination.

        Args:
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return await self._client.request_paginated(
            "GET", "/v1/api-keys", params=params
        )

    async def create(
        self,
        name: str,
        *,
        scopes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new API key.

        Args:
            name: Human-readable name for the key.
            scopes: Optional list of permission scopes.

        Returns:
            The created API key including the full key value
            (only returned once at creation time).
        """
        payload: Dict[str, Any] = {"name": name}
        if scopes is not None:
            payload["scopes"] = scopes
        return await self._client.request(
            "POST", "/v1/api-keys", json=payload
        )

    async def update_trust_level(
        self,
        key_id: str,
        level: str,
    ) -> Dict[str, Any]:
        """Update the trust level of an API key.

        Args:
            key_id: The API key ID.
            level: New trust level (review, trusted).

        Returns:
            The updated API key.
        """
        return await self._client.request(
            "PATCH",
            f"/v1/api-keys/{quote(key_id, safe='')}/trust",
            json={"trustLevel": level},
        )

    async def revoke(self, key_id: str) -> None:
        """Revoke (delete) an API key.

        Args:
            key_id: The API key ID to revoke.
        """
        await self._client.request(
            "DELETE", f"/v1/api-keys/{quote(key_id, safe='')}"
        )
