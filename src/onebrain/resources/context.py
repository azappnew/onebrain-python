from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict
from urllib.parse import quote

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class ContextResource:
    """Sync resource for OneBrain Context API (1 method)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def get(self, scope: str = "deep") -> Dict[str, Any]:
        """Retrieve optimized context for a given scope.

        Args:
            scope: Context scope level. One of 'brief', 'assistant',
                'project', or 'deep'. Defaults to 'deep'.

        Returns:
            Optimized context with formatted text, structured data,
            and metadata including token estimate.
        """
        return self._client.request(
            "GET", f"/v1/context/{quote(scope, safe='')}"
        )


class AsyncContextResource:
    """Async resource for OneBrain Context API (1 method)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def get(self, scope: str = "deep") -> Dict[str, Any]:
        """Retrieve optimized context for a given scope.

        Args:
            scope: Context scope level. One of 'brief', 'assistant',
                'project', or 'deep'. Defaults to 'deep'.

        Returns:
            Optimized context with formatted text, structured data,
            and metadata including token estimate.
        """
        return await self._client.request(
            "GET", f"/v1/context/{quote(scope, safe='')}"
        )
