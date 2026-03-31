"""Tests for onebrain.resources.api_keys — ApiKeysResource & AsyncApiKeysResource."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from onebrain.resources.api_keys import ApiKeysResource, AsyncApiKeysResource


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
    return ApiKeysResource(mock_client)


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
    return AsyncApiKeysResource(async_mock_client)


# ===================================================================
# Sync — ApiKeysResource.list
# ===================================================================


class TestApiKeysList:
    """Tests for ApiKeysResource.list()."""

    def test_list_no_params(self, resource, mock_client):
        result = resource.list()

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/api-keys", params={},
        )
        assert result == mock_client.request_paginated.return_value

    def test_list_with_cursor(self, resource, mock_client):
        resource.list(cursor="cur_123")

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/api-keys", params={"cursor": "cur_123"},
        )

    def test_list_with_limit(self, resource, mock_client):
        resource.list(limit=50)

        mock_client.request_paginated.assert_called_once_with(
            "GET", "/v1/api-keys", params={"limit": 50},
        )

    def test_list_with_cursor_and_limit(self, resource, mock_client):
        resource.list(cursor="page2", limit=10)

        mock_client.request_paginated.assert_called_once_with(
            "GET",
            "/v1/api-keys",
            params={"cursor": "page2", "limit": 10},
        )

    def test_list_returns_paginated_keys(self, resource, mock_client):
        expected = {
            "items": [
                {
                    "id": "key_1",
                    "name": "Production Key",
                    "prefix": "ob_prod",
                    "scopes": ["memory:read", "memory:write"],
                    "trust_level": "trusted",
                    "created_at": "2026-01-01T00:00:00Z",
                    "last_used_at": "2026-03-31T12:00:00Z",
                },
            ],
            "cursor": None,
            "has_more": False,
            "total": 1,
        }
        mock_client.request_paginated.return_value = expected

        result = resource.list()

        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "Production Key"


# ===================================================================
# Sync — ApiKeysResource.create
# ===================================================================


class TestApiKeysCreate:
    """Tests for ApiKeysResource.create()."""

    def test_create_with_name_only(self, resource, mock_client):
        mock_client.request.return_value = {
            "id": "key_new",
            "name": "Test Key",
            "full_key": "ob_test_xxx:secret",
        }

        result = resource.create("Test Key")

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/api-keys",
            json={"name": "Test Key"},
        )
        assert result["full_key"] == "ob_test_xxx:secret"

    def test_create_with_scopes(self, resource, mock_client):
        scopes = ["memory:read", "skills:read"]
        resource.create("Readonly Key", scopes=scopes)

        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/api-keys",
            json={"name": "Readonly Key", "scopes": scopes},
        )

    def test_create_without_scopes_excludes_key(
        self, resource, mock_client
    ):
        """When scopes is None, the key should not be in the payload."""
        resource.create("No Scopes Key", scopes=None)

        call_kwargs = mock_client.request.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][2]
        assert "scopes" not in payload

    def test_create_returns_full_key(self, resource, mock_client):
        mock_client.request.return_value = {
            "id": "key_abc",
            "name": "My Key",
            "prefix": "ob_my",
            "scopes": [],
            "trust_level": "review",
            "created_at": "2026-03-31T10:00:00Z",
            "last_used_at": None,
            "full_key": "ob_my_abc:full_secret_here",
        }

        result = resource.create("My Key")

        assert "full_key" in result
        assert result["trust_level"] == "review"


# ===================================================================
# Sync — ApiKeysResource.update_trust_level
# ===================================================================


class TestApiKeysUpdateTrustLevel:
    """Tests for ApiKeysResource.update_trust_level()."""

    def test_update_to_trusted(self, resource, mock_client):
        mock_client.request.return_value = {
            "id": "key_1",
            "trust_level": "trusted",
        }

        result = resource.update_trust_level("key_1", "trusted")

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/api-keys/key_1/trust",
            json={"trustLevel": "trusted"},
        )
        assert result["trust_level"] == "trusted"

    def test_update_to_review(self, resource, mock_client):
        resource.update_trust_level("key_2", "review")

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/api-keys/key_2/trust",
            json={"trustLevel": "review"},
        )

    def test_update_url_encodes_key_id(self, resource, mock_client):
        resource.update_trust_level("key/special", "trusted")

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/api-keys/key%2Fspecial/trust",
            json={"trustLevel": "trusted"},
        )

    @pytest.mark.parametrize("level", ["review", "trusted"])
    def test_update_all_trust_levels(self, resource, mock_client, level):
        resource.update_trust_level("key_x", level)

        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/api-keys/key_x/trust",
            json={"trustLevel": level},
        )


# ===================================================================
# Sync — ApiKeysResource.revoke
# ===================================================================


class TestApiKeysRevoke:
    """Tests for ApiKeysResource.revoke()."""

    def test_revoke_calls_delete(self, resource, mock_client):
        resource.revoke("key_to_delete")

        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/api-keys/key_to_delete",
        )

    def test_revoke_returns_none(self, resource, mock_client):
        mock_client.request.return_value = None

        result = resource.revoke("key_rm")

        assert result is None

    def test_revoke_url_encodes_key_id(self, resource, mock_client):
        resource.revoke("key/with spaces")

        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/api-keys/key%2Fwith%20spaces",
        )


# ===================================================================
# Async — AsyncApiKeysResource.list
# ===================================================================


class TestAsyncApiKeysList:
    """Tests for AsyncApiKeysResource.list()."""

    @pytest.mark.asyncio
    async def test_list_no_params(
        self, async_resource, async_mock_client
    ):
        result = await async_resource.list()

        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET", "/v1/api-keys", params={},
        )
        assert result == async_mock_client.request_paginated.return_value

    @pytest.mark.asyncio
    async def test_list_with_pagination(
        self, async_resource, async_mock_client
    ):
        await async_resource.list(cursor="async_cur", limit=20)

        async_mock_client.request_paginated.assert_awaited_once_with(
            "GET",
            "/v1/api-keys",
            params={"cursor": "async_cur", "limit": 20},
        )


# ===================================================================
# Async — AsyncApiKeysResource.create
# ===================================================================


class TestAsyncApiKeysCreate:
    """Tests for AsyncApiKeysResource.create()."""

    @pytest.mark.asyncio
    async def test_create_with_name(
        self, async_resource, async_mock_client
    ):
        async_mock_client.request.return_value = {
            "id": "akey_1",
            "name": "Async Key",
            "full_key": "ob_async:secret",
        }

        result = await async_resource.create("Async Key")

        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/api-keys",
            json={"name": "Async Key"},
        )
        assert result["full_key"] == "ob_async:secret"

    @pytest.mark.asyncio
    async def test_create_with_scopes(
        self, async_resource, async_mock_client
    ):
        await async_resource.create(
            "Scoped Key", scopes=["memory:read"]
        )

        async_mock_client.request.assert_awaited_once_with(
            "POST",
            "/v1/api-keys",
            json={"name": "Scoped Key", "scopes": ["memory:read"]},
        )


# ===================================================================
# Async — AsyncApiKeysResource.update_trust_level
# ===================================================================


class TestAsyncApiKeysUpdateTrustLevel:
    """Tests for AsyncApiKeysResource.update_trust_level()."""

    @pytest.mark.asyncio
    async def test_update_trust_level(
        self, async_resource, async_mock_client
    ):
        async_mock_client.request.return_value = {
            "id": "akey_1",
            "trust_level": "trusted",
        }

        result = await async_resource.update_trust_level(
            "akey_1", "trusted"
        )

        async_mock_client.request.assert_awaited_once_with(
            "PATCH",
            "/v1/api-keys/akey_1/trust",
            json={"trustLevel": "trusted"},
        )
        assert result["trust_level"] == "trusted"


# ===================================================================
# Async — AsyncApiKeysResource.revoke
# ===================================================================


class TestAsyncApiKeysRevoke:
    """Tests for AsyncApiKeysResource.revoke()."""

    @pytest.mark.asyncio
    async def test_revoke_calls_delete(
        self, async_resource, async_mock_client
    ):
        await async_resource.revoke("akey_del")

        async_mock_client.request.assert_awaited_once_with(
            "DELETE", "/v1/api-keys/akey_del",
        )

    @pytest.mark.asyncio
    async def test_revoke_returns_none(
        self, async_resource, async_mock_client
    ):
        async_mock_client.request.return_value = None

        result = await async_resource.revoke("akey_rm")

        assert result is None
