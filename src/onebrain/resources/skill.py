from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import quote

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class SkillResource:
    """Sync resource for OneBrain Skill API (3 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list(
        self,
        *,
        status: Optional[str] = None,
        min_confidence: Optional[float] = None,
        sort_by: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List skills with optional filtering and pagination.

        Args:
            status: Filter by skill status (candidate, active,
                archived, dismissed).
            min_confidence: Minimum confidence score filter.
            sort_by: Sort order (confidence, usage, recency).
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if min_confidence is not None:
            params["minConfidence"] = min_confidence
        if sort_by is not None:
            params["sortBy"] = sort_by
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return self._client.request_paginated(
            "GET", "/v1/skills", params=params
        )

    def get(self, skill_id: str) -> Dict[str, Any]:
        """Retrieve a single skill by ID.

        Args:
            skill_id: The skill ID.

        Returns:
            The skill object with title, body, status,
            confidence score, usage count, and trigger conditions.
        """
        return self._client.request(
            "GET", f"/v1/skills/{quote(skill_id, safe='')}"
        )

    def feedback(
        self,
        skill_id: str,
        event_type: str,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit feedback for a skill.

        Args:
            skill_id: The skill ID.
            event_type: Feedback event (applied, referenced,
                dismissed).
            context: Optional additional context for the feedback.

        Returns:
            Confirmation with recorded status.
        """
        payload: Dict[str, Any] = {"eventType": event_type}
        if context is not None:
            payload["context"] = context
        return self._client.request(
            "POST",
            f"/v1/skills/{quote(skill_id, safe='')}/feedback",
            json=payload,
        )


class AsyncSkillResource:
    """Async resource for OneBrain Skill API (3 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        status: Optional[str] = None,
        min_confidence: Optional[float] = None,
        sort_by: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List skills with optional filtering and pagination.

        Args:
            status: Filter by skill status (candidate, active,
                archived, dismissed).
            min_confidence: Minimum confidence score filter.
            sort_by: Sort order (confidence, usage, recency).
            cursor: Pagination cursor.
            limit: Max items to return (default 20, max 100).

        Returns:
            Paginated result with items, cursor, hasMore, and total.
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if min_confidence is not None:
            params["minConfidence"] = min_confidence
        if sort_by is not None:
            params["sortBy"] = sort_by
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        return await self._client.request_paginated(
            "GET", "/v1/skills", params=params
        )

    async def get(self, skill_id: str) -> Dict[str, Any]:
        """Retrieve a single skill by ID.

        Args:
            skill_id: The skill ID.

        Returns:
            The skill object with title, body, status,
            confidence score, usage count, and trigger conditions.
        """
        return await self._client.request(
            "GET", f"/v1/skills/{quote(skill_id, safe='')}"
        )

    async def feedback(
        self,
        skill_id: str,
        event_type: str,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit feedback for a skill.

        Args:
            skill_id: The skill ID.
            event_type: Feedback event (applied, referenced,
                dismissed).
            context: Optional additional context for the feedback.

        Returns:
            Confirmation with recorded status.
        """
        payload: Dict[str, Any] = {"eventType": event_type}
        if context is not None:
            payload["context"] = context
        return await self._client.request(
            "POST",
            f"/v1/skills/{quote(skill_id, safe='')}/feedback",
            json=payload,
        )
