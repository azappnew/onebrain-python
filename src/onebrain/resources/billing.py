from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .._client import BaseClient
    from .._async_client import AsyncBaseClient


class BillingResource:
    """Sync resource for OneBrain Billing API (2 methods)."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def usage(
        self,
        *,
        period: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve usage statistics for the current billing period.

        Args:
            period: Aggregation period (daily, weekly, monthly).
                Defaults to monthly on the server.

        Returns:
            Usage stats with period label and usage breakdown.
        """
        params: Dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        return self._client.request(
            "GET", "/v1/billing/usage", params=params
        )

    def plan(self) -> Dict[str, Any]:
        """Retrieve the current billing plan details.

        Returns:
            Plan details with name and limits.
        """
        return self._client.request("GET", "/v1/billing/plan")


class AsyncBillingResource:
    """Async resource for OneBrain Billing API (2 methods)."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client

    async def usage(
        self,
        *,
        period: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve usage statistics for the current billing period.

        Args:
            period: Aggregation period (daily, weekly, monthly).
                Defaults to monthly on the server.

        Returns:
            Usage stats with period label and usage breakdown.
        """
        params: Dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        return await self._client.request(
            "GET", "/v1/billing/usage", params=params
        )

    async def plan(self) -> Dict[str, Any]:
        """Retrieve the current billing plan details.

        Returns:
            Plan details with name and limits.
        """
        return await self._client.request("GET", "/v1/billing/plan")
