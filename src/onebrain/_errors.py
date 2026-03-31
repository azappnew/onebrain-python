from __future__ import annotations

from typing import Any, Optional


class OneBrainError(Exception):
    """Base exception for all OneBrain SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.append(f"code={self.code}")
        if self.status_code is not None:
            parts.append(f"status={self.status_code}")
        if self.request_id:
            parts.append(f"request_id={self.request_id}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"status_code={self.status_code!r})"
        )


class OneBrainAuthenticationError(OneBrainError):
    """Raised when the API returns a 401 Unauthorized response."""

    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=401, **kwargs)


class OneBrainPermissionError(OneBrainError):
    """Raised when the API returns a 403 Forbidden response."""

    def __init__(
        self,
        message: str = "Permission denied",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=403, **kwargs)


class OneBrainNotFoundError(OneBrainError):
    """Raised when the API returns a 404 Not Found response."""

    def __init__(
        self,
        message: str = "Resource not found",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=404, **kwargs)


class OneBrainRateLimitError(OneBrainError):
    """Raised when the API returns a 429 Too Many Requests response."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class OneBrainTimeoutError(OneBrainError):
    """Raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OneBrainNetworkError(OneBrainError):
    """Raised when a network connection fails."""

    def __init__(
        self,
        message: str = "Network connection failed",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OneBrainValidationError(OneBrainError):
    """Raised when the API returns a 400 or 422 validation error."""

    def __init__(
        self,
        message: str = "Validation error",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
