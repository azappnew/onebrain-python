"""Tests for onebrain.OneBrain and onebrain.AsyncOneBrain client classes.

These tests verify initialization, environment-variable resolution,
resource attribute wiring, context-manager behaviour, and repr output.
"""

from __future__ import annotations

import os
import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Bootstrap shims
#
# The SDK __init__.py references modules whose canonical location differs
# from the import path used:
#
#   onebrain._exceptions  ->  actual file is _errors.py
#   onebrain._base_client ->  sync client is in _client.py,
#                              async client is in _async_client.py
#
# We create lightweight module shims so the import chain succeeds.
# ---------------------------------------------------------------------------


def _ensure_shim_modules():
    """Register missing module aliases that __init__.py expects."""

    # --- onebrain._exceptions (alias for _errors) ---
    exc_key = "onebrain._exceptions"
    if exc_key not in sys.modules:
        try:
            from onebrain import _errors
        except ImportError:
            _errors = None

        if _errors is not None:
            shim = types.ModuleType(exc_key)
            for name in dir(_errors):
                if name.startswith("OneBrain"):
                    setattr(shim, name, getattr(_errors, name))
            for missing in (
                "OneBrainConflictError",
                "OneBrainConnectionError",
                "OneBrainInternalError",
            ):
                if not hasattr(shim, missing):
                    setattr(
                        shim,
                        missing,
                        type(missing, (_errors.OneBrainError,), {}),
                    )
            sys.modules[exc_key] = shim

    # --- onebrain._base_client (alias combining _client + _async_client) ---
    bc_key = "onebrain._base_client"
    if bc_key not in sys.modules:
        shim = types.ModuleType(bc_key)
        try:
            from onebrain._client import BaseClient
            shim.BaseClient = BaseClient
        except ImportError:
            pass
        try:
            from onebrain._async_client import AsyncBaseClient
            shim.AsyncBaseClient = AsyncBaseClient
        except ImportError:
            pass
        sys.modules[bc_key] = shim


_ensure_shim_modules()

# Now the real imports are safe.
from onebrain import AsyncOneBrain, OneBrain  # noqa: E402
from onebrain._errors import (  # noqa: E402
    OneBrainAuthenticationError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

API_KEY = "ob_test_key:secret"
CUSTOM_URL = "https://custom.onebrain.dev/api/v2"
DEFAULT_URL = "https://onebrain.rocks/api/eu"


def _make_mock_client(base_url=DEFAULT_URL, timeout=10.0):
    """Create a MagicMock that exposes ``base_url`` and ``timeout``.

    The real BaseClient stores these as ``_base_url`` and the httpx timeout,
    but OneBrain.__repr__ accesses ``self._client.base_url`` / ``.timeout``.
    This mock satisfies the repr contract.
    """
    mock = MagicMock()
    mock.base_url = base_url.rstrip("/")
    mock.timeout = timeout
    return mock


# ===================================================================
# OneBrain -- initialization
# ===================================================================


class TestOneBrainInit:
    """Tests for OneBrain.__init__."""

    def test_init_with_explicit_api_key(self):
        client = OneBrain(api_key=API_KEY)

        assert client._client is not None

    def test_init_stores_internal_client(self):
        client = OneBrain(api_key=API_KEY)

        from onebrain._client import BaseClient

        assert isinstance(client._client, BaseClient)

    def test_init_with_custom_max_retries(self):
        client = OneBrain(api_key=API_KEY, max_retries=5)

        assert client._client is not None

    def test_init_with_extra_headers(self):
        headers = {"X-Custom": "value"}
        client = OneBrain(api_key=API_KEY, headers=headers)

        assert client._client is not None

    def test_init_raises_without_api_key_and_no_env(self):
        env = {
            k: v for k, v in os.environ.items()
            if k != "ONEBRAIN_API_KEY"
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(OneBrainAuthenticationError):
                OneBrain()

    def test_init_reads_api_key_from_env(self):
        with patch.dict(
            os.environ, {"ONEBRAIN_API_KEY": "ob_env_key:secret"}
        ):
            client = OneBrain()

            assert client._client is not None

    def test_explicit_key_takes_precedence_over_env(self):
        with patch.dict(
            os.environ, {"ONEBRAIN_API_KEY": "ob_env:ignored"}
        ):
            client = OneBrain(api_key="ob_explicit:used")

            assert client._client is not None

    def test_init_with_default_timeout(self):
        client = OneBrain(api_key=API_KEY)

        assert client._client is not None

    def test_init_with_custom_timeout(self):
        client = OneBrain(api_key=API_KEY, timeout=30.0)

        assert client._client is not None

    def test_init_with_custom_base_url(self):
        client = OneBrain(api_key=API_KEY, base_url=CUSTOM_URL)

        assert client._client is not None


# ===================================================================
# OneBrain -- resource attributes
# ===================================================================


class TestOneBrainResources:
    """Tests that all resource attributes are present and correctly typed."""

    @pytest.fixture()
    def client(self):
        return OneBrain(api_key=API_KEY)

    RESOURCE_NAMES = [
        "memory",
        "entity",
        "project",
        "brain",
        "context",
        "connect",
        "billing",
        "api_keys",
        "skill",
        "briefing",
    ]

    @pytest.mark.parametrize("attr", RESOURCE_NAMES)
    def test_resource_attribute_exists(self, client, attr):
        assert hasattr(client, attr), f"Missing resource attribute: {attr}"

    @pytest.mark.parametrize("attr", RESOURCE_NAMES)
    def test_resource_attribute_is_not_none(self, client, attr):
        assert getattr(client, attr) is not None

    def test_billing_is_billing_resource(self, client):
        from onebrain.resources.billing import BillingResource

        assert isinstance(client.billing, BillingResource)

    def test_api_keys_is_api_keys_resource(self, client):
        from onebrain.resources.api_keys import ApiKeysResource

        assert isinstance(client.api_keys, ApiKeysResource)

    def test_skill_is_skill_resource(self, client):
        from onebrain.resources.skill import SkillResource

        assert isinstance(client.skill, SkillResource)

    def test_briefing_is_briefing_resource(self, client):
        from onebrain.resources.briefing import BriefingResource

        assert isinstance(client.briefing, BriefingResource)

    def test_resources_share_same_internal_client(self, client):
        assert client.billing._client is client._client
        assert client.api_keys._client is client._client
        assert client.skill._client is client._client
        assert client.briefing._client is client._client


# ===================================================================
# OneBrain -- context manager
# ===================================================================


class TestOneBrainContextManager:
    """Tests for the ``with OneBrain(...) as ob:`` protocol."""

    def test_enter_returns_self(self):
        client = OneBrain(api_key=API_KEY)

        result = client.__enter__()

        assert result is client

    def test_exit_calls_close(self):
        client = OneBrain(api_key=API_KEY)
        client._client = MagicMock()

        client.__exit__()

        client._client.close.assert_called_once()

    def test_with_block(self):
        with OneBrain(api_key=API_KEY) as client:
            assert client is not None
            assert hasattr(client, "memory")

    def test_close_delegates_to_internal_client(self):
        client = OneBrain(api_key=API_KEY)
        client._client = MagicMock()

        client.close()

        client._client.close.assert_called_once()

    def test_close_can_be_called_twice(self):
        client = OneBrain(api_key=API_KEY)
        client._client = MagicMock()

        client.close()
        client.close()

        assert client._client.close.call_count == 2


# ===================================================================
# OneBrain -- repr
# ===================================================================


class TestOneBrainRepr:
    """Tests for OneBrain.__repr__.

    The __repr__ accesses self._client.base_url and .timeout which the
    underlying BaseClient exposes as private attrs (_base_url). We
    substitute a mock so the repr path is exercised cleanly.
    """

    def test_repr_contains_class_name(self):
        client = OneBrain(api_key=API_KEY)
        client._client = _make_mock_client()

        assert "OneBrain(" in repr(client)

    def test_repr_contains_base_url(self):
        client = OneBrain(api_key=API_KEY)
        client._client = _make_mock_client(base_url=CUSTOM_URL)

        assert CUSTOM_URL.rstrip("/") in repr(client)

    def test_repr_contains_timeout(self):
        client = OneBrain(api_key=API_KEY)
        client._client = _make_mock_client(timeout=42.0)

        assert "42.0" in repr(client)

    def test_repr_does_not_leak_api_key(self):
        client = OneBrain(api_key="ob_secret_key:supersecret")
        client._client = _make_mock_client()

        representation = repr(client)

        assert "ob_secret_key" not in representation
        assert "supersecret" not in representation

    def test_repr_is_str(self):
        client = OneBrain(api_key=API_KEY)
        client._client = _make_mock_client()

        assert isinstance(repr(client), str)


# ===================================================================
# AsyncOneBrain -- initialization
# ===================================================================


class TestAsyncOneBrainInit:
    """Tests for AsyncOneBrain.__init__."""

    def test_init_with_explicit_api_key(self):
        client = AsyncOneBrain(api_key=API_KEY)

        assert client._client is not None

    def test_init_stores_async_base_client(self):
        client = AsyncOneBrain(api_key=API_KEY)

        from onebrain._async_client import AsyncBaseClient

        assert isinstance(client._client, AsyncBaseClient)

    def test_init_with_custom_base_url(self):
        client = AsyncOneBrain(api_key=API_KEY, base_url=CUSTOM_URL)

        assert client._client is not None

    def test_init_with_custom_timeout(self):
        client = AsyncOneBrain(api_key=API_KEY, timeout=25.0)

        assert client._client is not None

    def test_init_raises_without_api_key_and_no_env(self):
        env = {
            k: v for k, v in os.environ.items()
            if k != "ONEBRAIN_API_KEY"
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(OneBrainAuthenticationError):
                AsyncOneBrain()

    def test_init_reads_api_key_from_env(self):
        with patch.dict(
            os.environ, {"ONEBRAIN_API_KEY": "ob_async_env:secret"}
        ):
            client = AsyncOneBrain()

            assert client._client is not None

    def test_explicit_key_over_env(self):
        with patch.dict(
            os.environ, {"ONEBRAIN_API_KEY": "ob_env:nope"}
        ):
            client = AsyncOneBrain(api_key="ob_explicit:yes")

            assert client._client is not None

    def test_init_with_extra_headers(self):
        client = AsyncOneBrain(
            api_key=API_KEY, headers={"X-Trace": "abc"},
        )

        assert client._client is not None

    def test_init_with_custom_max_retries(self):
        client = AsyncOneBrain(api_key=API_KEY, max_retries=0)

        assert client._client is not None

    def test_init_default_base_url(self):
        client = AsyncOneBrain(api_key=API_KEY)

        assert client._client is not None


# ===================================================================
# AsyncOneBrain -- resource attributes
# ===================================================================


class TestAsyncOneBrainResources:
    """Tests that all async resource attributes exist and are typed."""

    @pytest.fixture()
    def client(self):
        return AsyncOneBrain(api_key=API_KEY)

    RESOURCE_NAMES = [
        "memory",
        "entity",
        "project",
        "brain",
        "context",
        "connect",
        "billing",
        "api_keys",
        "skill",
        "briefing",
    ]

    @pytest.mark.parametrize("attr", RESOURCE_NAMES)
    def test_resource_attribute_exists(self, client, attr):
        assert hasattr(client, attr), f"Missing resource: {attr}"

    @pytest.mark.parametrize("attr", RESOURCE_NAMES)
    def test_resource_attribute_is_not_none(self, client, attr):
        assert getattr(client, attr) is not None

    def test_billing_is_async_billing_resource(self, client):
        from onebrain.resources.billing import AsyncBillingResource

        assert isinstance(client.billing, AsyncBillingResource)

    def test_api_keys_is_async_api_keys_resource(self, client):
        from onebrain.resources.api_keys import AsyncApiKeysResource

        assert isinstance(client.api_keys, AsyncApiKeysResource)

    def test_skill_is_async_skill_resource(self, client):
        from onebrain.resources.skill import AsyncSkillResource

        assert isinstance(client.skill, AsyncSkillResource)

    def test_briefing_is_async_briefing_resource(self, client):
        from onebrain.resources.briefing import AsyncBriefingResource

        assert isinstance(client.briefing, AsyncBriefingResource)

    def test_resources_share_same_internal_client(self, client):
        assert client.billing._client is client._client
        assert client.api_keys._client is client._client
        assert client.skill._client is client._client
        assert client.briefing._client is client._client


# ===================================================================
# AsyncOneBrain -- async context manager
# ===================================================================


class TestAsyncOneBrainContextManager:
    """Tests for the ``async with AsyncOneBrain(...) as ob:`` protocol."""

    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        client = AsyncOneBrain(api_key=API_KEY)

        result = await client.__aenter__()

        assert result is client

    @pytest.mark.asyncio
    async def test_aexit_calls_aclose(self):
        client = AsyncOneBrain(api_key=API_KEY)
        client._client = AsyncMock()

        await client.__aexit__()

        client._client.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_async_with_block(self):
        client = AsyncOneBrain(api_key=API_KEY)
        client._client = AsyncMock()

        async with client as ob:
            assert ob is client
            assert hasattr(ob, "memory")

    @pytest.mark.asyncio
    async def test_aclose_delegates_to_client(self):
        client = AsyncOneBrain(api_key=API_KEY)
        client._client = AsyncMock()

        await client.aclose()

        client._client.aclose.assert_awaited_once()


# ===================================================================
# AsyncOneBrain -- repr
# ===================================================================


class TestAsyncOneBrainRepr:
    """Tests for AsyncOneBrain.__repr__."""

    def test_repr_contains_class_name(self):
        client = AsyncOneBrain(api_key=API_KEY)
        client._client = _make_mock_client()

        assert "AsyncOneBrain(" in repr(client)

    def test_repr_contains_base_url(self):
        client = AsyncOneBrain(api_key=API_KEY)
        client._client = _make_mock_client(base_url=CUSTOM_URL)

        assert CUSTOM_URL.rstrip("/") in repr(client)

    def test_repr_does_not_leak_api_key(self):
        client = AsyncOneBrain(api_key="ob_secret:topsecret")
        client._client = _make_mock_client()

        representation = repr(client)

        assert "ob_secret" not in representation
        assert "topsecret" not in representation

    def test_repr_is_str(self):
        client = AsyncOneBrain(api_key=API_KEY)
        client._client = _make_mock_client()

        assert isinstance(repr(client), str)

    def test_repr_contains_timeout(self):
        client = AsyncOneBrain(api_key=API_KEY)
        client._client = _make_mock_client(timeout=25.0)

        assert "25.0" in repr(client)
