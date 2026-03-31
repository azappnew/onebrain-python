"""OneBrain SDK — persistent AI memory layer for humans and agents.

Usage::

    import onebrain

    client = onebrain.OneBrain(api_key="ob_xxx:secret")
    memories = client.memory.list(limit=10)

Or with async::

    async with onebrain.AsyncOneBrain() as client:
        memories = await client.memory.list(limit=10)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Dict, Optional

from onebrain._version import __version__
from onebrain._exceptions import (
    OneBrainError,
    OneBrainAuthenticationError,
    OneBrainPermissionError,
    OneBrainNotFoundError,
    OneBrainConflictError,
    OneBrainValidationError,
    OneBrainRateLimitError,
    OneBrainConnectionError,
    OneBrainTimeoutError,
    OneBrainInternalError,
)

if TYPE_CHECKING:
    from onebrain._base_client import BaseClient, AsyncBaseClient
    from onebrain.resources.memory import MemoryResource, AsyncMemoryResource
    from onebrain.resources.entity import EntityResource, AsyncEntityResource
    from onebrain.resources.project import ProjectResource, AsyncProjectResource
    from onebrain.resources.brain import BrainResource, AsyncBrainResource
    from onebrain.resources.context import ContextResource, AsyncContextResource
    from onebrain.resources.connect import ConnectResource, AsyncConnectResource
    from onebrain.resources.billing import BillingResource, AsyncBillingResource
    from onebrain.resources.api_keys import ApiKeysResource, AsyncApiKeysResource
    from onebrain.resources.skill import SkillResource, AsyncSkillResource
    from onebrain.resources.briefing import BriefingResource, AsyncBriefingResource


class OneBrain:
    """OneBrain SDK client — persistent AI memory layer.

    Args:
        api_key: API key for authentication. Falls back to the
            ``ONEBRAIN_API_KEY`` environment variable when *None*.
        base_url: Base URL of the OneBrain API.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of automatic retries on transient errors.
        headers: Extra HTTP headers sent with every request.

    Raises:
        OneBrainAuthenticationError: If no API key is provided and
            ``ONEBRAIN_API_KEY`` is not set.

    Example::

        client = OneBrain(api_key="ob_xxx:secret")
        memories = client.memory.list(limit=5)
        client.close()

    Or as a context manager::

        with OneBrain() as client:
            memories = client.memory.list(limit=5)
    """

    memory: MemoryResource
    entity: EntityResource
    project: ProjectResource
    brain: BrainResource
    context: ContextResource
    connect: ConnectResource
    billing: BillingResource
    api_keys: ApiKeysResource
    skill: SkillResource
    briefing: BriefingResource

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = "https://onebrain.rocks/api/eu",
        timeout: float = 10.0,
        max_retries: int = 2,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        resolved_key = api_key or os.environ.get("ONEBRAIN_API_KEY")
        if resolved_key is None:
            raise OneBrainAuthenticationError(
                "No API key provided. Pass api_key= or set the "
                "ONEBRAIN_API_KEY environment variable. "
                "Create one at https://onebrain.rocks/dashboard/api-keys"
            )

        from onebrain._base_client import BaseClient
        from onebrain.resources.memory import MemoryResource
        from onebrain.resources.entity import EntityResource
        from onebrain.resources.project import ProjectResource
        from onebrain.resources.brain import BrainResource
        from onebrain.resources.context import ContextResource
        from onebrain.resources.connect import ConnectResource
        from onebrain.resources.billing import BillingResource
        from onebrain.resources.api_keys import ApiKeysResource
        from onebrain.resources.skill import SkillResource
        from onebrain.resources.briefing import BriefingResource

        self._client: BaseClient = BaseClient(
            api_key=resolved_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )

        self.memory = MemoryResource(self._client)
        self.entity = EntityResource(self._client)
        self.project = ProjectResource(self._client)
        self.brain = BrainResource(self._client)
        self.context = ContextResource(self._client)
        self.connect = ConnectResource(self._client)
        self.billing = BillingResource(self._client)
        self.api_keys = ApiKeysResource(self._client)
        self.skill = SkillResource(self._client)
        self.briefing = BriefingResource(self._client)

    def close(self) -> None:
        """Close the underlying HTTP transport and release resources."""
        self._client.close()

    def __enter__(self) -> "OneBrain":
        return self

    def __exit__(
        self,
        exc_type: Optional[type] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[object] = None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            f"OneBrain(base_url={self._client.base_url!r}, "
            f"timeout={self._client.timeout})"
        )


class AsyncOneBrain:
    """Async OneBrain SDK client — persistent AI memory layer.

    Args:
        api_key: API key for authentication. Falls back to the
            ``ONEBRAIN_API_KEY`` environment variable when *None*.
        base_url: Base URL of the OneBrain API.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of automatic retries on transient errors.
        headers: Extra HTTP headers sent with every request.

    Raises:
        OneBrainAuthenticationError: If no API key is provided and
            ``ONEBRAIN_API_KEY`` is not set.

    Example::

        async with AsyncOneBrain(api_key="ob_xxx:secret") as client:
            memories = await client.memory.list(limit=5)
    """

    memory: AsyncMemoryResource
    entity: AsyncEntityResource
    project: AsyncProjectResource
    brain: AsyncBrainResource
    context: AsyncContextResource
    connect: AsyncConnectResource
    billing: AsyncBillingResource
    api_keys: AsyncApiKeysResource
    skill: AsyncSkillResource
    briefing: AsyncBriefingResource

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = "https://onebrain.rocks/api/eu",
        timeout: float = 10.0,
        max_retries: int = 2,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        resolved_key = api_key or os.environ.get("ONEBRAIN_API_KEY")
        if resolved_key is None:
            raise OneBrainAuthenticationError(
                "No API key provided. Pass api_key= or set the "
                "ONEBRAIN_API_KEY environment variable. "
                "Create one at https://onebrain.rocks/dashboard/api-keys"
            )

        from onebrain._base_client import AsyncBaseClient
        from onebrain.resources.memory import AsyncMemoryResource
        from onebrain.resources.entity import AsyncEntityResource
        from onebrain.resources.project import AsyncProjectResource
        from onebrain.resources.brain import AsyncBrainResource
        from onebrain.resources.context import AsyncContextResource
        from onebrain.resources.connect import AsyncConnectResource
        from onebrain.resources.billing import AsyncBillingResource
        from onebrain.resources.api_keys import AsyncApiKeysResource
        from onebrain.resources.skill import AsyncSkillResource
        from onebrain.resources.briefing import AsyncBriefingResource

        self._client: AsyncBaseClient = AsyncBaseClient(
            api_key=resolved_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )

        self.memory = AsyncMemoryResource(self._client)
        self.entity = AsyncEntityResource(self._client)
        self.project = AsyncProjectResource(self._client)
        self.brain = AsyncBrainResource(self._client)
        self.context = AsyncContextResource(self._client)
        self.connect = AsyncConnectResource(self._client)
        self.billing = AsyncBillingResource(self._client)
        self.api_keys = AsyncApiKeysResource(self._client)
        self.skill = AsyncSkillResource(self._client)
        self.briefing = AsyncBriefingResource(self._client)

    async def aclose(self) -> None:
        """Close the underlying async HTTP transport and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncOneBrain":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[object] = None,
    ) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return (
            f"AsyncOneBrain(base_url={self._client.base_url!r}, "
            f"timeout={self._client.timeout})"
        )


__all__ = [
    "__version__",
    # Clients
    "OneBrain",
    "AsyncOneBrain",
    # Errors
    "OneBrainError",
    "OneBrainAuthenticationError",
    "OneBrainPermissionError",
    "OneBrainNotFoundError",
    "OneBrainConflictError",
    "OneBrainValidationError",
    "OneBrainRateLimitError",
    "OneBrainConnectionError",
    "OneBrainTimeoutError",
    "OneBrainInternalError",
]
