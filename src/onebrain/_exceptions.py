"""Compatibility shim — re-exports from _errors with aliases expected by __init__.py."""

from __future__ import annotations

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

# Aliases expected by __init__.py but not present in _errors.py
OneBrainConflictError = type(
    "OneBrainConflictError", (OneBrainError,), {}
)
OneBrainConnectionError = OneBrainNetworkError
OneBrainInternalError = type(
    "OneBrainInternalError", (OneBrainError,), {}
)

__all__ = [
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
