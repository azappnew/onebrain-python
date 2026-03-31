from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class BrainResource:
    """Sync resource for OneBrain Brain API (3 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def profile(self) -> Dict[str, Any]:
        """Retrieve the brain profile.

        Returns:
            Brain profile with summary, traits, and preferences.
        """
        return self._client.request("GET", "/v1/brain/profile")

    def update_profile(
        self,
        *,
        summary: Optional[str] = None,
        traits: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update the brain profile.

        Args:
            summary: Updated profile summary text.
            traits: Updated personality traits dict.
            preferences: Updated user preferences dict.

        Returns:
            The updated brain profile.
        """
        payload: Dict[str, Any] = {}
        if summary is not None:
            payload["summary"] = summary
        if traits is not None:
            payload["traits"] = traits
        if preferences is not None:
            payload["preferences"] = preferences
        return self._client.request(
            "PUT", "/v1/brain/profile", json=payload
        )

    def context(self) -> Dict[str, Any]:
        """Retrieve the full brain context.

        Returns:
            Brain context with formatted text, structured data,
            and metadata including token estimate.
        """
        return self._client.request("GET", "/v1/brain/context")


class AsyncBrainResource:
    """Async resource for OneBrain Brain API (3 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def profile(self) -> Dict[str, Any]:
        """Retrieve the brain profile.

        Returns:
            Brain profile with summary, traits, and preferences.
        """
        return await self._client.request("GET", "/v1/brain/profile")

    async def update_profile(
        self,
        *,
        summary: Optional[str] = None,
        traits: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update the brain profile.

        Args:
            summary: Updated profile summary text.
            traits: Updated personality traits dict.
            preferences: Updated user preferences dict.

        Returns:
            The updated brain profile.
        """
        payload: Dict[str, Any] = {}
        if summary is not None:
            payload["summary"] = summary
        if traits is not None:
            payload["traits"] = traits
        if preferences is not None:
            payload["preferences"] = preferences
        return await self._client.request(
            "PUT", "/v1/brain/profile", json=payload
        )

    async def context(self) -> Dict[str, Any]:
        """Retrieve the full brain context.

        Returns:
            Brain context with formatted text, structured data,
            and metadata including token estimate.
        """
        return await self._client.request("GET", "/v1/brain/context")
