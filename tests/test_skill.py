"""Tests for onebrain.resources.skill — SkillResource & AsyncSkillResource."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call

import pytest

from onebrain.resources.skill import AsyncSkillResource, SkillResource


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_client():
    """Return a MagicMock that mimics BaseClient."""
    client = MagicMock()
    client.request.return_value = {}
    client.request_paginated.return_value = {
        "items": [],
        "cursor": None,
        "has_more": False,
        "total": 0,
    }
    return client


@pytest.fixture()
def resource(mock_client):
    return SkillResource(mock_client)


@pytest.fixture()
def async_mock_client():
    """Return an AsyncMock that mimics AsyncBaseClient."""
    client = AsyncMock()
    client.request.return_value = {}
    client.request_paginated.return_value = {
        "items": [],
        "cursor": None,
        "has_more": False,
        "total": 0,
    }
    return client


@pytest.fixture()
def async_resource(async_mock_client):
    return AsyncSkillResource(async_mock_client)


# ===================================================================
# Sync — SkillResource.list
# ===================================================================


class TestSkillList:
    """Tests for SkillResource.list()."""

    def test_list_no_params(self, resource, mock_client):
        result = resource.list()

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/skills", params={},
        )
        assert result == mock_client.request_paginated.return_value

    def test_list_with_status_filter(self, resource, mock_client):
        resource.list(status="active")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/skills", params={"status": "active"},
        )

    def test_list_with_min_confidence(self, resource, mock_client):
        resource.list(min_confidence=0.8)

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/skills", params={"minConfidence": 0.8},
        )

    def test_list_with_sort_by(self, resource, mock_client):
        resource.list(sort_by="confidence")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/skills", params={"sortBy": "confidence"},
        )

    def test_list_with_pagination(self, resource, mock_client):
        resource.list(cursor="abc123", limit=50)

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/skills",
            params={"cursor": "abc123", "limit": 50},
        )

    def test_list_with_all_params(self, resource, mock_client):
        resource.list(
            status="candidate",
            min_confidence=0.5,
            sort_by="usage",
            cursor="xyz",
            limit=10,
        )

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/skills",
            params={
                "status": "candidate",
                "minConfidence": 0.5,
                "sortBy": "usage",
                "cursor": "xyz",
                "limit": 10,
            },
        )

    def test_list_returns_paginated_data(self, resource, mock_client):
        expected = {
            "items": [{"id": "sk_1", "title": "Python patterns"}],
            "cursor": "next_page",
            "has_more": True,
            "total": 42,
        }
        mock_client.request_paginated.return_value = expected

        result = resource.list()

        assert result["items"] == [{"id": "sk_1", "title": "Python patterns"}]
        assert result["has_more"] is True
        assert result["total"] == 42


# ===================================================================
# Sync — SkillResource.get
# ===================================================================


class TestSkillGet:
    """Tests for SkillResource.get()."""

    def test_get_by_id(self, resource, mock_client):
        mock_client.request.return_value = {
            "id": "sk_abc",
            "title": "Error handling",
            "status": "active",
        }

        result = resource.get("sk_abc")

        mock_client.request.assert_called_once_with(
            "GET", "/v1/skills/sk_abc",
        )
        assert result["id"] == "sk_abc"

    def test_get_url_encodes_special_chars(self, resource, mock_client):
        resource.get("sk/special id")

        mock_client.request.assert_called_once_with(
            "GET", "/v1/skills/sk%2Fspecial%20id",
        )

    def test_get_returns_full_skill_object(self, resource, mock_client):
        full_skill = {
            "id": "sk_1",
            "title": "Async patterns",
            "body": "Use async/await for I/O-bound ops.",
            "status": "active",
            "confidence_score": 0.95,
            "usage_count": 12,
            "trigger_conditions": ["async", "concurrency"],
        }
        mock_client.request.return_value = full_skill

        result = resource.get("sk_1")

        assert result == full_skill


# ===================================================================
# Sync — SkillResource.feedback
# ===================================================================


class TestSkillFeedback:
    """Tests for SkillResource.feedback()."""

    def test_feedback_minimal(self, resource, mock_client):
        mock_client.request.return_value = {"status": "recorded"}

        result = resource.feedback("sk_abc", "applied")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/skills/sk_abc/feedback",
            json={"eventType": "applied"},
        )
        assert result["status"] == "recorded"

    def test_feedback_with_context(self, resource, mock_client):
        ctx = {"session_id": "sess_1", "query": "How to handle errors?"}
        resource.feedback("sk_abc", "referenced", context=ctx)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/skills/sk_abc/feedback",
            json={
                "eventType": "referenced",
                "context": ctx,
            },
        )

    def test_feedback_dismissed_event(self, resource, mock_client):
        resource.feedback("sk_xyz", "dismissed")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/skills/sk_xyz/feedback",
            json={"eventType": "dismissed"},
        )

    def test_feedback_url_encodes_skill_id(self, resource, mock_client):
        resource.feedback("sk/special", "applied")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/skills/sk%2Fspecial/feedback",
            json={"eventType": "applied"},
        )

    @pytest.mark.parametrize(
        "event_type",
        ["applied", "referenced", "dismissed"],
    )
    def test_feedback_all_event_types(
        self, resource, mock_client, event_type
    ):
        resource.feedback("sk_1", event_type)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/skills/sk_1/feedback",
            json={"eventType": event_type},
        )


# ===================================================================
# Async — AsyncSkillResource.list
# ===================================================================


class TestAsyncSkillList:
    """Tests for AsyncSkillResource.list()."""

    @pytest.mark.asyncio
    async def test_list_no_params(self, async_resource, async_mock_client):
        result = await async_resource.list()

        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET", "/v1/skills", params={},
        )
        assert result == async_mock_client.request_paginated.return_value

    @pytest.mark.asyncio
    async def test_list_with_all_params(
        self, async_resource, async_mock_client
    ):
        await async_resource.list(
            status="archived",
            min_confidence=0.3,
            sort_by="recency",
            cursor="page2",
            limit=25,
        )

        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET",
            "/v1/skills",
            params={
                "status": "archived",
                "minConfidence": 0.3,
                "sortBy": "recency",
                "cursor": "page2",
                "limit": 25,
            },
        )


# ===================================================================
# Async — AsyncSkillResource.get
# ===================================================================


class TestAsyncSkillGet:
    """Tests for AsyncSkillResource.get()."""

    @pytest.mark.asyncio
    async def test_get_by_id(self, async_resource, async_mock_client):
        async_mock_client.request.return_value = {
            "id": "sk_async",
            "title": "Async skill",
        }

        result = await async_resource.get("sk_async")

        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/skills/sk_async",
        )
        assert result["id"] == "sk_async"

    @pytest.mark.asyncio
    async def test_get_url_encodes_id(
        self, async_resource, async_mock_client
    ):
        await async_resource.get("id with spaces")

        async_mock_client.request.assert_awaited_once_with(
            "GET", "/v1/skills/id%20with%20spaces",
        )


# ===================================================================
# Async — AsyncSkillResource.feedback
# ===================================================================


class TestAsyncSkillFeedback:
    """Tests for AsyncSkillResource.feedback()."""

    @pytest.mark.asyncio
    async def test_feedback_minimal(
        self, async_resource, async_mock_client
    ):
        async_mock_client.request.return_value = {"status": "recorded"}

        result = await async_resource.feedback("sk_1", "applied")

        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/skills/sk_1/feedback",
            json={"eventType": "applied"},
        )
        assert result["status"] == "recorded"

    @pytest.mark.asyncio
    async def test_feedback_with_context(
        self, async_resource, async_mock_client
    ):
        ctx = {"tool": "code-editor"}
        await async_resource.feedback("sk_1", "referenced", context=ctx)

        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/skills/sk_1/feedback",
            json={"eventType": "referenced", "context": ctx},
        )
