"""Tests for AsyncBaseClient — mirrors test_client.py for async coverage."""
from __future__ import annotations

import pytest
import httpx
import respx

from onebrain._async_client import AsyncBaseClient, _parse_retry_after
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


API_KEY = "ob_test_key_12345"
BASE = "https://api.onebrain.ai"


@pytest.fixture
def aclient():
    return AsyncBaseClient(api_key=API_KEY, base_url=BASE, max_retries=0)


# ── Init ──────────────────────────────────────────────


class TestAsyncClientInit:
    def test_stores_base_url(self):
        c = AsyncBaseClient(api_key=API_KEY, base_url="https://x.com/")
        assert c._base_url == "https://x.com"

    def test_strips_trailing_slash(self):
        c = AsyncBaseClient(api_key=API_KEY, base_url="https://x.com///")
        assert c._base_url == "https://x.com"

    def test_empty_key_raises(self):
        with pytest.raises(OneBrainAuthenticationError):
            AsyncBaseClient(api_key="")

    def test_whitespace_key_raises(self):
        with pytest.raises(OneBrainAuthenticationError):
            AsyncBaseClient(api_key="   ")

    def test_custom_headers_merged(self):
        c = AsyncBaseClient(
            api_key=API_KEY, headers={"X-Custom": "val"}
        )
        assert c._client.headers["x-custom"] == "val"
        assert "apikey" in c._client.headers["authorization"].lower()

    def test_default_max_retries(self):
        c = AsyncBaseClient(api_key=API_KEY)
        assert c._max_retries == 2


# ── Context Manager ───────────────────────────────────


class TestAsyncContextManager:
    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        c = AsyncBaseClient(api_key=API_KEY)
        assert await c.__aenter__() is c
        await c.aclose()

    @pytest.mark.asyncio
    async def test_async_with_block(self):
        async with AsyncBaseClient(api_key=API_KEY) as c:
            assert isinstance(c, AsyncBaseClient)


# ── build_query ───────────────────────────────────────


class TestBuildQuery:
    def test_filters_none(self):
        c = AsyncBaseClient(api_key=API_KEY)
        assert c.build_query({"a": 1, "b": None}) == {"a": 1}

    def test_keeps_falsy(self):
        c = AsyncBaseClient(api_key=API_KEY)
        assert c.build_query({"a": 0, "b": "", "c": False}) == {
            "a": 0,
            "b": "",
            "c": False,
        }

    def test_empty_dict(self):
        c = AsyncBaseClient(api_key=API_KEY)
        assert c.build_query({}) == {}


# ── Successful requests ──────────────────────────────


class TestAsyncSuccessfulRequests:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_unwraps_data(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                200, json={"data": {"id": "1"}, "meta": {}}
            )
        )
        result = await aclient.request("GET", "/v1/test")
        assert result == {"id": "1"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_post_with_body(self, aclient):
        respx.post(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                201, json={"data": {"id": "new"}}
            )
        )
        result = await aclient.request(
            "POST", "/v1/test", body={"name": "x"}
        )
        assert result == {"id": "new"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_put_request(self, aclient):
        respx.put(f"{BASE}/v1/test/1").mock(
            return_value=httpx.Response(200, json={"data": "ok"})
        )
        result = await aclient.request(
            "PUT", "/v1/test/1", body={"name": "y"}
        )
        assert result == "ok"

    @pytest.mark.asyncio
    @respx.mock
    async def test_patch_request(self, aclient):
        respx.patch(f"{BASE}/v1/test/1").mock(
            return_value=httpx.Response(200, json={"data": "patched"})
        )
        result = await aclient.request(
            "PATCH", "/v1/test/1", body={"name": "z"}
        )
        assert result == "patched"

    @pytest.mark.asyncio
    @respx.mock
    async def test_delete_204(self, aclient):
        respx.delete(f"{BASE}/v1/test/1").mock(
            return_value=httpx.Response(204)
        )
        result = await aclient.request("DELETE", "/v1/test/1")
        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_with_params(self, aclient):
        route = respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        await aclient.request(
            "GET", "/v1/test", params={"limit": 10, "cursor": "abc"}
        )
        assert route.called
        req = route.calls[0].request
        assert "limit=10" in str(req.url)
        assert "cursor=abc" in str(req.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_none_params_filtered(self, aclient):
        route = respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        await aclient.request(
            "GET", "/v1/test", params={"a": "1", "b": None}
        )
        req = route.calls[0].request
        assert "a=1" in str(req.url)
        assert "b=" not in str(req.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_non_envelope_returned_as_is(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(200, json=[1, 2, 3])
        )
        result = await aclient.request("GET", "/v1/test")
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    @respx.mock
    async def test_invalid_json_returns_empty(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                200, content=b"not json", headers={"content-type": "text/plain"}
            )
        )
        result = await aclient.request("GET", "/v1/test")
        assert result == {}


# ── Paginated requests ────────────────────────────────


class TestAsyncPaginatedRequests:
    @pytest.mark.asyncio
    @respx.mock
    async def test_items_format(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "items": [{"id": "1"}],
                        "cursor": "c1",
                        "hasMore": True,
                        "total": 50,
                    }
                },
            )
        )
        result = await aclient.request_paginated("/v1/test")
        assert result["items"] == [{"id": "1"}]
        assert result["cursor"] == "c1"
        assert result["has_more"] is True
        assert result["total"] == 50

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_fallback(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                200, json={"data": [{"id": "1"}, {"id": "2"}]}
            )
        )
        result = await aclient.request_paginated("/v1/test")
        assert result["items"] == [{"id": "1"}, {"id": "2"}]
        assert result["has_more"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_scalar_fallback(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(200, json={"data": "scalar"})
        )
        result = await aclient.request_paginated("/v1/test")
        assert result["items"] == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_params_forwarded(self, aclient):
        route = respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        await aclient.request_paginated(
            "/v1/test", params={"limit": 5}
        )
        assert "limit=5" in str(route.calls[0].request.url)


# ── Error mapping ─────────────────────────────────────


class TestAsyncErrorMapping:
    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize(
        "status,exc_class",
        [
            (401, OneBrainAuthenticationError),
            (403, OneBrainPermissionError),
            (404, OneBrainNotFoundError),
            (429, OneBrainRateLimitError),
            (400, OneBrainValidationError),
            (422, OneBrainValidationError),
        ],
    )
    async def test_status_maps_to_error(self, aclient, status, exc_class):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                status,
                json={"error": {"code": "ERR", "message": "fail"}},
            )
        )
        with pytest.raises(exc_class):
            await aclient.request("GET", "/v1/test")

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_raises_generic(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                500,
                json={"error": {"code": "INTERNAL", "message": "boom"}},
            )
        )
        with pytest.raises(OneBrainError) as exc_info:
            await aclient.request("GET", "/v1/test")
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_id_extracted(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                404,
                json={
                    "error": {"code": "NOT_FOUND", "message": "gone"},
                    "meta": {"requestId": "req-123"},
                },
            )
        )
        with pytest.raises(OneBrainNotFoundError) as exc_info:
            await aclient.request("GET", "/v1/test")
        assert exc_info.value.request_id == "req-123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_details_extracted(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                422,
                json={
                    "error": {
                        "code": "VALIDATION",
                        "message": "bad",
                        "details": [{"field": "name"}],
                    }
                },
            )
        )
        with pytest.raises(OneBrainValidationError) as exc_info:
            await aclient.request("GET", "/v1/test")
        assert exc_info.value.details == [{"field": "name"}]

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_payload_fallback(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(500, content=b"")
        )
        with pytest.raises(OneBrainError):
            await aclient.request("GET", "/v1/test")

    @pytest.mark.asyncio
    @respx.mock
    async def test_retry_after_header(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                429,
                json={"error": {"code": "RATE_LIMITED", "message": "slow"}},
                headers={"retry-after": "30"},
            )
        )
        with pytest.raises(OneBrainRateLimitError) as exc_info:
            await aclient.request("GET", "/v1/test")
        assert exc_info.value.retry_after == 30.0


# ── Transport errors ──────────────────────────────────


class TestAsyncTransportErrors:
    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_raises(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            side_effect=httpx.ReadTimeout("timeout")
        )
        with pytest.raises(OneBrainTimeoutError):
            await aclient.request("GET", "/v1/test")

    @pytest.mark.asyncio
    @respx.mock
    async def test_connect_error_raises(self, aclient):
        respx.get(f"{BASE}/v1/test").mock(
            side_effect=httpx.ConnectError("refused")
        )
        with pytest.raises(OneBrainNetworkError):
            await aclient.request("GET", "/v1/test")


# ── Retry logic ───────────────────────────────────────


class TestAsyncRetryLogic:
    @pytest.mark.asyncio
    @respx.mock
    async def test_retries_on_500(self):
        c = AsyncBaseClient(api_key=API_KEY, base_url=BASE, max_retries=1)
        route = respx.get(f"{BASE}/v1/test")
        route.side_effect = [
            httpx.Response(
                500,
                json={"error": {"code": "ERR", "message": "fail"}},
            ),
            httpx.Response(200, json={"data": "ok"}),
        ]
        result = await c.request("GET", "/v1/test")
        assert result == "ok"
        assert route.call_count == 2
        await c.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_retries_on_429(self):
        c = AsyncBaseClient(api_key=API_KEY, base_url=BASE, max_retries=1)
        route = respx.get(f"{BASE}/v1/test")
        route.side_effect = [
            httpx.Response(
                429,
                json={"error": {"code": "RATE", "message": "slow"}},
                headers={"retry-after": "0.01"},
            ),
            httpx.Response(200, json={"data": "ok"}),
        ]
        result = await c.request("GET", "/v1/test")
        assert result == "ok"
        assert route.call_count == 2
        await c.aclose()

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
    async def test_no_retry_on_4xx(self, aclient, status):
        route = respx.get(f"{BASE}/v1/test")
        route.mock(
            return_value=httpx.Response(
                status,
                json={"error": {"code": "ERR", "message": "fail"}},
            )
        )
        with pytest.raises(OneBrainError):
            await aclient.request("GET", "/v1/test")
        assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_exhausted_retries_raises(self):
        c = AsyncBaseClient(api_key=API_KEY, base_url=BASE, max_retries=2)
        respx.get(f"{BASE}/v1/test").mock(
            return_value=httpx.Response(
                502,
                json={"error": {"code": "BAD_GW", "message": "down"}},
            )
        )
        with pytest.raises(OneBrainError) as exc_info:
            await c.request("GET", "/v1/test")
        assert exc_info.value.status_code == 502
        await c.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_not_retried(self, aclient):
        route = respx.get(f"{BASE}/v1/test")
        route.mock(side_effect=httpx.ReadTimeout("timeout"))
        with pytest.raises(OneBrainTimeoutError):
            await aclient.request("GET", "/v1/test")
        assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_network_error_not_retried(self, aclient):
        route = respx.get(f"{BASE}/v1/test")
        route.mock(side_effect=httpx.ConnectError("refused"))
        with pytest.raises(OneBrainNetworkError):
            await aclient.request("GET", "/v1/test")
        assert route.call_count == 1


# ── parse_retry_after ─────────────────────────────────


class TestParseRetryAfter:
    def test_valid_int(self):
        resp = httpx.Response(429, headers={"retry-after": "5"})
        assert _parse_retry_after(resp) == 5.0

    def test_valid_float(self):
        resp = httpx.Response(429, headers={"retry-after": "1.5"})
        assert _parse_retry_after(resp) == 1.5

    def test_missing_header(self):
        resp = httpx.Response(429)
        assert _parse_retry_after(resp) is None

    def test_invalid_value(self):
        resp = httpx.Response(429, headers={"retry-after": "abc"})
        assert _parse_retry_after(resp) is None
