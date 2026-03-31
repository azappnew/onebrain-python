from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx

from ._errors import (
    OneBrainAuthenticationError,
    OneBrainError,
    OneBrainNetworkError,
    OneBrainNotFoundError,
    OneBrainPermissionError,
    OneBrainRateLimitError,
    OneBrainTimeoutError,
    OneBrainValidationError,
)
from ._types import PaginatedResult


_DEFAULT_BASE_URL = "https://onebrain.rocks/api/eu"
_DEFAULT_TIMEOUT = 10.0
_DEFAULT_MAX_RETRIES = 2
_INITIAL_BACKOFF = 0.5


class AsyncBaseClient:
    """Asynchronous HTTP client for the OneBrain API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise OneBrainAuthenticationError(
                "API key must not be empty",
                code="MISSING_API_KEY",
            )

        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries

        default_headers = {
            "Authorization": f"ApiKey {api_key}",
            "Content-Type": "application/json",
            "X-Requested-With": "OneBrainPythonSDK",
        }
        if headers:
            default_headers.update(headers)

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=default_headers,
            timeout=timeout,
        )

    # ── Public API ─────────────────────────────────────────

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute an HTTP request and return the unwrapped data payload."""
        query = self.build_query(params) if params else None
        return await self._request_with_retry(
            method, path, body=body, params=query
        )

    async def request_paginated(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResult:
        """Execute a GET request and return a PaginatedResult."""
        query = self.build_query(params) if params else None
        raw = await self._request_with_retry("GET", path, params=query)

        if isinstance(raw, dict) and "items" in raw:
            return {
                "items": raw.get("items", []),
                "cursor": raw.get("cursor"),
                "has_more": raw.get("hasMore", False),
                "total": raw.get("total"),
            }

        return {
            "items": raw if isinstance(raw, list) else [],
            "cursor": None,
            "has_more": False,
            "total": None,
        }

    def build_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out None values from query parameters."""
        return {
            key: value
            for key, value in params.items()
            if value is not None
        }

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncBaseClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    # ── Internal helpers ───────────────────────────────────

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        last_error: Optional[Exception] = None
        attempts = self._max_retries + 1

        for attempt in range(attempts):
            try:
                return await self._execute(
                    method, path, body=body, params=params
                )
            except OneBrainRateLimitError as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    raise
                wait = (
                    exc.retry_after
                    if exc.retry_after
                    else _INITIAL_BACKOFF * (2 ** attempt)
                )
                await asyncio.sleep(wait)
            except OneBrainError as exc:
                last_error = exc
                if (
                    exc.status_code is not None
                    and 500 <= exc.status_code < 600
                ):
                    if attempt >= self._max_retries:
                        raise
                    await asyncio.sleep(_INITIAL_BACKOFF * (2 ** attempt))
                else:
                    raise
            except (OneBrainTimeoutError, OneBrainNetworkError):
                raise

        raise last_error  # type: ignore[misc]

    async def _execute(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            response = await self._client.request(
                method,
                path,
                json=body,
                params=params,
            )
        except httpx.TimeoutException as exc:
            raise OneBrainTimeoutError(
                f"Request timed out: {method} {path}"
            ) from exc
        except httpx.ConnectError as exc:
            raise OneBrainNetworkError(
                f"Connection failed: {method} {path}"
            ) from exc

        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 204:
            return None

        try:
            payload = response.json()
        except Exception:
            payload = {}

        request_id = (
            payload.get("meta", {}).get("requestId")
            if isinstance(payload, dict)
            else None
        )

        if response.status_code >= 400:
            self._raise_for_status(response, payload, request_id)

        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]

        return payload

    def _raise_for_status(
        self,
        response: httpx.Response,
        payload: Any,
        request_id: Optional[str],
    ) -> None:
        error_body = (
            payload.get("error", {}) if isinstance(payload, dict) else {}
        )
        code = error_body.get("code", "UNKNOWN_ERROR")
        message = error_body.get(
            "message", response.reason_phrase or "Unknown error"
        )
        details = error_body.get("details")
        status = response.status_code

        common = dict(
            code=code,
            details=details,
            request_id=request_id,
        )

        if status == 401:
            raise OneBrainAuthenticationError(message, **common)
        if status == 403:
            raise OneBrainPermissionError(message, **common)
        if status == 404:
            raise OneBrainNotFoundError(message, **common)
        if status == 429:
            retry_after = _parse_retry_after(response)
            raise OneBrainRateLimitError(
                message, retry_after=retry_after, **common
            )
        if status in (400, 422):
            raise OneBrainValidationError(
                message, status_code=status, **common
            )

        raise OneBrainError(
            message, status_code=status, **common
        )


def _parse_retry_after(response: httpx.Response) -> Optional[float]:
    """Parse the Retry-After header value as seconds."""
    value = response.headers.get("retry-after")
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
