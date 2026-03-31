"""Tests for onebrain._client — BaseClient HTTP behavior, retries, and error mapping."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx

from onebrain._client import (
    BaseClient,
    _DEFAULT_BASE_URL,
    _DEFAULT_MAX_RETRIES,
    _DEFAULT_TIMEOUT,
    _INITIAL_BACKOFF,
    _parse_retry_after,
)
from onebrain._errors import (
    OneBrainAuthenticationError,
    OneBrainError,
    OneBrainNetworkError,
    OneBrainNotFoundError,
    OneBrainPermissionError,
    OneBrainRateLimitError,
    OneBrainTimeoutError,
    OneBrainValidationError,
)


# ── Initialization ────────────────────────────────────────


class TestClientInit:
    """Test BaseClient constructor behavior."""

    def test_stores_base_url(self, api_key, base_url):
        client = BaseClient(api_key=api_key, base_url=base_url)
        assert client._base_url == base_url

    def test_strips_trailing_slash_from_base_url(self, api_key):
        client = BaseClient(
            api_key=api_key, base_url="https://api.example.com/"
        )
        assert client._base_url == "https://api.example.com"

    def test_strips_multiple_trailing_slashes(self, api_key):
        client = BaseClient(
            api_key=api_key, base_url="https://api.example.com///"
        )
        assert client._base_url == "https://api.example.com"

    def test_default_base_url(self, api_key):
        client = BaseClient(api_key=api_key)
        assert client._base_url == _DEFAULT_BASE_URL.rstrip("/")

    def test_default_max_retries(self, api_key):
        client = BaseClient(api_key=api_key)
        assert client._max_retries == _DEFAULT_MAX_RETRIES

    def test_custom_max_retries(self, api_key):
        client = BaseClient(api_key=api_key, max_retries=5)
        assert client._max_retries == 5

    def test_rejects_empty_api_key(self):
        with pytest.raises(OneBrainAuthenticationError, match="must not be empty"):
            BaseClient(api_key="")

    def test_rejects_whitespace_only_api_key(self):
        with pytest.raises(OneBrainAuthenticationError, match="must not be empty"):
            BaseClient(api_key="   ")

    def test_rejects_empty_string_api_key_has_code(self):
        with pytest.raises(OneBrainAuthenticationError) as exc_info:
            BaseClient(api_key="")
        assert exc_info.value.code == "MISSING_API_KEY"


class TestDefaultHeaders:
    """Test that the httpx client is configured with correct default headers."""

    def test_authorization_header(self, client, api_key):
        headers = client._client.headers
        assert headers["authorization"] == f"ApiKey {api_key}"

    def test_content_type_header(self, client):
        headers = client._client.headers
        assert headers["content-type"] == "application/json"

    def test_x_requested_with_header(self, client):
        headers = client._client.headers
        assert headers["x-requested-with"] == "OneBrainPythonSDK"

    def test_custom_headers_merged(self, api_key, base_url):
        client = BaseClient(
            api_key=api_key,
            base_url=base_url,
            headers={"X-Custom": "value"},
        )
        assert client._client.headers["x-custom"] == "value"

    def test_custom_headers_override_defaults(self, api_key, base_url):
        client = BaseClient(
            api_key=api_key,
            base_url=base_url,
            headers={"Content-Type": "text/plain"},
        )
        assert client._client.headers["content-type"] == "text/plain"


class TestClientTimeout:
    """Test timeout configuration."""

    def test_default_timeout(self, api_key):
        client = BaseClient(api_key=api_key)
        assert client._client.timeout.read == _DEFAULT_TIMEOUT

    def test_custom_timeout(self, api_key):
        client = BaseClient(api_key=api_key, timeout=30.0)
        assert client._client.timeout.read == 30.0


# ── Context manager ───────────────────────────────────────


class TestContextManager:
    """Test __enter__ / __exit__ behavior."""

    def test_enter_returns_self(self, client):
        with client as ctx:
            assert ctx is client

    def test_exit_closes_client(self, api_key, base_url):
        client = BaseClient(api_key=api_key, base_url=base_url)
        client.close()
        assert client._client.is_closed

    def test_context_manager_closes_on_exit(self, api_key, base_url):
        client = BaseClient(api_key=api_key, base_url=base_url)
        with client:
            pass
        assert client._client.is_closed


# ── build_query ───────────────────────────────────────────


class TestBuildQuery:
    """Test query parameter filtering."""

    def test_removes_none_values(self, client):
        result = client.build_query({"a": 1, "b": None, "c": "x"})
        assert result == {"a": 1, "c": "x"}

    def test_keeps_falsy_non_none_values(self, client):
        result = client.build_query({"a": 0, "b": "", "c": False})
        assert result == {"a": 0, "b": "", "c": False}

    def test_empty_dict_returns_empty(self, client):
        assert client.build_query({}) == {}

    def test_all_none_returns_empty(self, client):
        assert client.build_query({"a": None, "b": None}) == {}


# ── Successful requests ──────────────────────────────────


class TestSuccessfulRequests:
    """Test successful HTTP responses with the envelope format."""

    @respx.mock
    def test_get_unwraps_data_envelope(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(
                200,
                json={"data": [{"id": "m1"}], "meta": {}},
            )
        )
        result = client.request("GET", "/v1/memories")
        assert result == [{"id": "m1"}]

    @respx.mock
    def test_post_unwraps_data_envelope(self, client):
        respx.post(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(
                201,
                json={"data": {"id": "m2", "title": "new"}},
            )
        )
        result = client.request("POST", "/v1/memories", body={"title": "new"})
        assert result == {"id": "m2", "title": "new"}

    @respx.mock
    def test_put_request(self, client):
        respx.put(
            "https://api.onebrain.ai/v1/memories/m1"
        ).mock(
            return_value=httpx.Response(
                200,
                json={"data": {"id": "m1", "title": "updated"}},
            )
        )
        result = client.request(
            "PUT", "/v1/memories/m1", body={"title": "updated"}
        )
        assert result == {"id": "m1", "title": "updated"}

    @respx.mock
    def test_patch_request(self, client):
        respx.patch(
            "https://api.onebrain.ai/v1/memories/m1"
        ).mock(
            return_value=httpx.Response(
                200,
                json={"data": {"id": "m1", "status": "archived"}},
            )
        )
        result = client.request(
            "PATCH", "/v1/memories/m1", body={"status": "archived"}
        )
        assert result["status"] == "archived"

    @respx.mock
    def test_delete_returns_none_on_204(self, client):
        respx.delete(
            "https://api.onebrain.ai/v1/memories/m1"
        ).mock(
            return_value=httpx.Response(204)
        )
        result = client.request("DELETE", "/v1/memories/m1")
        assert result is None

    @respx.mock
    def test_response_without_data_key_returns_full_payload(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/health"
        ).mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        result = client.request("GET", "/v1/health")
        assert result == {"status": "ok"}

    @respx.mock
    def test_query_params_forwarded(self, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client.request(
            "GET", "/v1/memories", params={"limit": 10, "type": "fact"}
        )
        assert route.called
        request = route.calls.last.request
        assert "limit=10" in str(request.url)
        assert "type=fact" in str(request.url)

    @respx.mock
    def test_none_params_filtered_out(self, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client.request(
            "GET", "/v1/memories",
            params={"limit": 5, "cursor": None},
        )
        request = route.calls.last.request
        assert "limit=5" in str(request.url)
        assert "cursor" not in str(request.url)

    @respx.mock
    def test_empty_json_body_parsed_as_empty_dict(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                200, content=b"not json", headers={"content-type": "text/plain"}
            )
        )
        result = client.request("GET", "/v1/test")
        assert result == {}

    @respx.mock
    def test_request_with_no_params_skips_query(self, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client.request("GET", "/v1/memories")
        request = route.calls.last.request
        assert "?" not in str(request.url)


# ── Paginated requests ───────────────────────────────────


class TestPaginatedRequests:
    """Test request_paginated envelope parsing."""

    @respx.mock
    def test_paginated_with_items_key(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "items": [{"id": "m1"}],
                        "cursor": "abc",
                        "hasMore": True,
                        "total": 42,
                    },
                },
            )
        )
        result = client.request_paginated("/v1/memories")
        assert result["items"] == [{"id": "m1"}]
        assert result["cursor"] == "abc"
        assert result["has_more"] is True
        assert result["total"] == 42

    @respx.mock
    def test_paginated_fallback_for_list_response(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(
                200,
                json={"data": [{"id": "m1"}, {"id": "m2"}]},
            )
        )
        result = client.request_paginated("/v1/memories")
        assert result["items"] == [{"id": "m1"}, {"id": "m2"}]
        assert result["cursor"] is None
        assert result["has_more"] is False
        assert result["total"] is None

    @respx.mock
    def test_paginated_fallback_for_non_list_non_dict(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/something"
        ).mock(
            return_value=httpx.Response(200, json={"data": "scalar_val"})
        )
        result = client.request_paginated("/v1/something")
        assert result["items"] == []

    @respx.mock
    def test_paginated_forwards_params(self, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/memories"
        ).mock(
            return_value=httpx.Response(
                200,
                json={"data": {"items": [], "hasMore": False}},
            )
        )
        client.request_paginated(
            "/v1/memories", params={"limit": 5, "status": "active"}
        )
        request = route.calls.last.request
        assert "limit=5" in str(request.url)


# ── Error response mapping ───────────────────────────────


class TestErrorMapping:
    """Test HTTP status -> SDK error class mapping."""

    @respx.mock
    @pytest.mark.parametrize(
        "status,error_cls",
        [
            (401, OneBrainAuthenticationError),
            (403, OneBrainPermissionError),
            (404, OneBrainNotFoundError),
            (429, OneBrainRateLimitError),
            (400, OneBrainValidationError),
            (422, OneBrainValidationError),
        ],
        ids=["401", "403", "404", "429", "400", "422"],
    )
    def test_status_to_error_mapping(self, client, status, error_cls):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                status,
                json={
                    "error": {
                        "code": "TEST_ERROR",
                        "message": "test message",
                    },
                },
            )
        )
        with pytest.raises(error_cls) as exc_info:
            client.request("GET", "/v1/test")
        assert exc_info.value.code == "TEST_ERROR"
        assert exc_info.value.message == "test message"

    @respx.mock
    def test_500_raises_generic_onebrain_error(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                500,
                json={
                    "error": {
                        "code": "INTERNAL",
                        "message": "server error",
                    },
                },
            )
        )
        with pytest.raises(OneBrainError) as exc_info:
            client.request("GET", "/v1/test")
        assert exc_info.value.status_code == 500

    @respx.mock
    def test_error_includes_request_id_from_meta(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                404,
                json={
                    "error": {"code": "NOT_FOUND", "message": "gone"},
                    "meta": {"requestId": "req-xyz"},
                },
            )
        )
        with pytest.raises(OneBrainNotFoundError) as exc_info:
            client.request("GET", "/v1/test")
        assert exc_info.value.request_id == "req-xyz"

    @respx.mock
    def test_error_includes_details(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                422,
                json={
                    "error": {
                        "code": "VALIDATION",
                        "message": "invalid",
                        "details": [{"field": "title"}],
                    },
                },
            )
        )
        with pytest.raises(OneBrainValidationError) as exc_info:
            client.request("GET", "/v1/test")
        assert exc_info.value.details == [{"field": "title"}]

    @respx.mock
    def test_error_with_empty_payload(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                500,
                content=b"Internal Server Error",
                headers={"content-type": "text/plain"},
            )
        )
        with pytest.raises(OneBrainError) as exc_info:
            client.request("GET", "/v1/test")
        assert exc_info.value.status_code == 500
        assert exc_info.value.code == "UNKNOWN_ERROR"

    @respx.mock
    def test_429_with_retry_after_header(self, client):
        client._max_retries = 0
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                429,
                json={"error": {"code": "RATE_LIMIT", "message": "slow"}},
                headers={"Retry-After": "30"},
            )
        )
        with pytest.raises(OneBrainRateLimitError) as exc_info:
            client.request("GET", "/v1/test")
        assert exc_info.value.retry_after == 30.0

    @respx.mock
    def test_unknown_4xx_raises_generic_error(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                418,
                json={"error": {"code": "TEAPOT", "message": "I am a teapot"}},
            )
        )
        with pytest.raises(OneBrainError) as exc_info:
            client.request("GET", "/v1/test")
        assert exc_info.value.status_code == 418


# ── Timeout and network errors ───────────────────────────


class TestTransportErrors:
    """Test timeout and connection error handling."""

    @respx.mock
    def test_timeout_raises_onebrain_timeout_error(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(side_effect=httpx.ReadTimeout("timed out"))
        with pytest.raises(OneBrainTimeoutError, match="timed out"):
            client.request("GET", "/v1/test")

    @respx.mock
    def test_connect_error_raises_onebrain_network_error(self, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(side_effect=httpx.ConnectError("refused"))
        with pytest.raises(OneBrainNetworkError, match="Connection failed"):
            client.request("GET", "/v1/test")

    @respx.mock
    def test_timeout_error_not_retried(self, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(side_effect=httpx.ReadTimeout("timeout"))
        with pytest.raises(OneBrainTimeoutError):
            client.request("GET", "/v1/test")
        assert route.call_count == 1

    @respx.mock
    def test_network_error_not_retried(self, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(side_effect=httpx.ConnectError("down"))
        with pytest.raises(OneBrainNetworkError):
            client.request("GET", "/v1/test")
        assert route.call_count == 1


# ── Retry logic ──────────────────────────────────────────


class TestRetryLogic:
    """Test automatic retry on 5xx and 429 errors."""

    @respx.mock
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_retries_on_500(self, mock_sleep, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                500,
                json={"error": {"code": "INTERNAL", "message": "fail"}},
            )
        )
        with pytest.raises(OneBrainError):
            client.request("GET", "/v1/test")
        assert route.call_count == _DEFAULT_MAX_RETRIES + 1

    @respx.mock
    @pytest.mark.parametrize("status", [500, 502, 503, 504], ids=str)
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_retries_on_5xx_statuses(self, mock_sleep, client, status):
        route = respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                status,
                json={"error": {"code": "SERVER", "message": "err"}},
            )
        )
        with pytest.raises(OneBrainError):
            client.request("GET", "/v1/test")
        assert route.call_count == _DEFAULT_MAX_RETRIES + 1

    @respx.mock
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_retries_on_429(self, mock_sleep, client):
        route = respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                429,
                json={
                    "error": {"code": "RATE_LIMIT", "message": "slow down"},
                },
            )
        )
        with pytest.raises(OneBrainRateLimitError):
            client.request("GET", "/v1/test")
        assert route.call_count == _DEFAULT_MAX_RETRIES + 1

    @respx.mock
    @pytest.mark.parametrize("status", [400, 401, 403, 404, 422], ids=str)
    def test_does_not_retry_on_4xx(self, client, status):
        route = respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                status,
                json={"error": {"code": "CLIENT", "message": "nope"}},
            )
        )
        with pytest.raises(OneBrainError):
            client.request("GET", "/v1/test")
        assert route.call_count == 1

    @respx.mock
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_retry_succeeds_on_second_attempt(self, mock_sleep, client):
        route = respx.get("https://api.onebrain.ai/v1/test")
        route.side_effect = [
            httpx.Response(
                503,
                json={"error": {"code": "UNAVAILABLE", "message": "retry"}},
            ),
            httpx.Response(200, json={"data": {"ok": True}}),
        ]
        result = client.request("GET", "/v1/test")
        assert result == {"ok": True}
        assert route.call_count == 2

    @respx.mock
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_retry_backoff_timing(self, mock_sleep, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                500,
                json={"error": {"code": "ERR", "message": "fail"}},
            )
        )
        with pytest.raises(OneBrainError):
            client.request("GET", "/v1/test")
        calls = mock_sleep.call_args_list
        assert len(calls) == _DEFAULT_MAX_RETRIES
        assert calls[0].args[0] == _INITIAL_BACKOFF * (2 ** 0)
        assert calls[1].args[0] == _INITIAL_BACKOFF * (2 ** 1)

    @respx.mock
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_429_retry_uses_retry_after_header(self, mock_sleep, client):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                429,
                json={"error": {"code": "RATE", "message": "wait"}},
                headers={"Retry-After": "15"},
            )
        )
        with pytest.raises(OneBrainRateLimitError):
            client.request("GET", "/v1/test")
        first_sleep = mock_sleep.call_args_list[0].args[0]
        assert first_sleep == 15.0

    @respx.mock
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_429_retry_falls_back_to_exponential_without_header(
        self, mock_sleep, client
    ):
        respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                429,
                json={"error": {"code": "RATE", "message": "wait"}},
            )
        )
        with pytest.raises(OneBrainRateLimitError):
            client.request("GET", "/v1/test")
        first_sleep = mock_sleep.call_args_list[0].args[0]
        assert first_sleep == _INITIAL_BACKOFF

    @respx.mock
    @patch("onebrain._client.time.sleep", return_value=None)
    def test_max_retries_zero_means_no_retry(self, mock_sleep, api_key, base_url):
        client = BaseClient(
            api_key=api_key, base_url=base_url, max_retries=0
        )
        route = respx.get(
            "https://api.onebrain.ai/v1/test"
        ).mock(
            return_value=httpx.Response(
                500,
                json={"error": {"code": "INTERNAL", "message": "err"}},
            )
        )
        with pytest.raises(OneBrainError):
            client.request("GET", "/v1/test")
        assert route.call_count == 1
        mock_sleep.assert_not_called()


# ── _parse_retry_after helper ────────────────────────────


class TestParseRetryAfter:
    """Test the Retry-After header parser."""

    def test_parses_integer_value(self):
        response = httpx.Response(429, headers={"Retry-After": "60"})
        assert _parse_retry_after(response) == 60.0

    def test_parses_float_value(self):
        response = httpx.Response(429, headers={"Retry-After": "1.5"})
        assert _parse_retry_after(response) == 1.5

    def test_returns_none_when_header_missing(self):
        response = httpx.Response(429)
        assert _parse_retry_after(response) is None

    def test_returns_none_for_invalid_value(self):
        response = httpx.Response(
            429, headers={"Retry-After": "not-a-number"}
        )
        assert _parse_retry_after(response) is None

    def test_returns_none_for_empty_value(self):
        response = httpx.Response(429, headers={"Retry-After": ""})
        assert _parse_retry_after(response) is None
