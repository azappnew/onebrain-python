"""Tests for onebrain._errors — all error classes, hierarchy, and behavior."""

from __future__ import annotations

import pytest

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


# ── Inheritance hierarchy ──────────────────────────────────


@pytest.mark.parametrize(
    "error_cls",
    [
        OneBrainAuthenticationError,
        OneBrainPermissionError,
        OneBrainNotFoundError,
        OneBrainRateLimitError,
        OneBrainTimeoutError,
        OneBrainNetworkError,
        OneBrainValidationError,
    ],
    ids=lambda c: c.__name__,
)
class TestInheritance:
    """All subclasses must inherit from OneBrainError and Exception."""

    def test_inherits_from_onebrain_error(self, error_cls):
        assert issubclass(error_cls, OneBrainError)

    def test_inherits_from_exception(self, error_cls):
        assert issubclass(error_cls, Exception)

    def test_instance_is_catchable_as_onebrain_error(self, error_cls):
        with pytest.raises(OneBrainError):
            raise error_cls()

    def test_instance_is_catchable_as_exception(self, error_cls):
        with pytest.raises(Exception):
            raise error_cls()


# ── OneBrainError (base) ──────────────────────────────────


class TestOneBrainError:
    """Tests for the base OneBrainError class."""

    def test_message_stored(self):
        err = OneBrainError("something broke")
        assert err.message == "something broke"

    def test_default_code_is_none(self):
        err = OneBrainError("msg")
        assert err.code is None

    def test_default_status_code_is_none(self):
        err = OneBrainError("msg")
        assert err.status_code is None

    def test_default_details_is_none(self):
        err = OneBrainError("msg")
        assert err.details is None

    def test_default_request_id_is_none(self):
        err = OneBrainError("msg")
        assert err.request_id is None

    def test_all_kwargs_stored(self):
        err = OneBrainError(
            "msg",
            code="ERR_CODE",
            status_code=500,
            details=["field_x invalid"],
            request_id="req-abc-123",
        )
        assert err.code == "ERR_CODE"
        assert err.status_code == 500
        assert err.details == ["field_x invalid"]
        assert err.request_id == "req-abc-123"

    def test_str_message_only(self):
        err = OneBrainError("simple message")
        assert str(err) == "simple message"

    def test_str_with_code(self):
        err = OneBrainError("msg", code="ERR")
        assert str(err) == "msg | code=ERR"

    def test_str_with_status_code(self):
        err = OneBrainError("msg", status_code=404)
        assert str(err) == "msg | status=404"

    def test_str_with_request_id(self):
        err = OneBrainError("msg", request_id="req-1")
        assert str(err) == "msg | request_id=req-1"

    def test_str_with_all_parts(self):
        err = OneBrainError(
            "fail", code="X", status_code=500, request_id="r-99"
        )
        result = str(err)
        assert result == "fail | code=X | status=500 | request_id=r-99"

    def test_str_does_not_include_details(self):
        err = OneBrainError("msg", details={"a": 1})
        assert "details" not in str(err)

    def test_repr_format(self):
        err = OneBrainError("boom", code="C", status_code=418)
        expected = (
            "OneBrainError(message='boom', code='C', status_code=418)"
        )
        assert repr(err) == expected

    def test_repr_with_none_values(self):
        err = OneBrainError("x")
        assert repr(err) == (
            "OneBrainError(message='x', code=None, status_code=None)"
        )

    def test_exception_args_contain_message(self):
        err = OneBrainError("hello")
        assert err.args == ("hello",)


# ── OneBrainAuthenticationError ───────────────────────────


class TestAuthenticationError:
    def test_default_message(self):
        err = OneBrainAuthenticationError()
        assert err.message == "Authentication failed"

    def test_custom_message(self):
        err = OneBrainAuthenticationError("Invalid token")
        assert err.message == "Invalid token"

    def test_status_code_always_401(self):
        err = OneBrainAuthenticationError()
        assert err.status_code == 401

    def test_kwargs_forwarded(self):
        err = OneBrainAuthenticationError(
            code="TOKEN_EXPIRED", request_id="r-1"
        )
        assert err.code == "TOKEN_EXPIRED"
        assert err.request_id == "r-1"


# ── OneBrainPermissionError ──────────────────────────────


class TestPermissionError:
    def test_default_message(self):
        err = OneBrainPermissionError()
        assert err.message == "Permission denied"

    def test_custom_message(self):
        err = OneBrainPermissionError("Admin required")
        assert err.message == "Admin required"

    def test_status_code_always_403(self):
        err = OneBrainPermissionError()
        assert err.status_code == 403

    def test_kwargs_forwarded(self):
        err = OneBrainPermissionError(
            code="FORBIDDEN", details={"role": "user"}
        )
        assert err.code == "FORBIDDEN"
        assert err.details == {"role": "user"}


# ── OneBrainNotFoundError ────────────────────────────────


class TestNotFoundError:
    def test_default_message(self):
        err = OneBrainNotFoundError()
        assert err.message == "Resource not found"

    def test_custom_message(self):
        err = OneBrainNotFoundError("Memory item abc not found")
        assert err.message == "Memory item abc not found"

    def test_status_code_always_404(self):
        err = OneBrainNotFoundError()
        assert err.status_code == 404


# ── OneBrainRateLimitError ───────────────────────────────


class TestRateLimitError:
    def test_default_message(self):
        err = OneBrainRateLimitError()
        assert err.message == "Rate limit exceeded"

    def test_custom_message(self):
        err = OneBrainRateLimitError("Too fast")
        assert err.message == "Too fast"

    def test_status_code_always_429(self):
        err = OneBrainRateLimitError()
        assert err.status_code == 429

    def test_default_retry_after_is_none(self):
        err = OneBrainRateLimitError()
        assert err.retry_after is None

    def test_retry_after_stored(self):
        err = OneBrainRateLimitError(retry_after=30.0)
        assert err.retry_after == 30.0

    def test_retry_after_with_kwargs(self):
        err = OneBrainRateLimitError(
            "slow down", retry_after=5.0, code="RATE_LIMIT"
        )
        assert err.retry_after == 5.0
        assert err.code == "RATE_LIMIT"
        assert err.status_code == 429


# ── OneBrainTimeoutError ─────────────────────────────────


class TestTimeoutError:
    def test_default_message(self):
        err = OneBrainTimeoutError()
        assert err.message == "Request timed out"

    def test_custom_message(self):
        err = OneBrainTimeoutError("Gateway timed out after 30s")
        assert err.message == "Gateway timed out after 30s"

    def test_default_status_code_is_none(self):
        err = OneBrainTimeoutError()
        assert err.status_code is None

    def test_kwargs_forwarded(self):
        err = OneBrainTimeoutError(code="TIMEOUT")
        assert err.code == "TIMEOUT"


# ── OneBrainNetworkError ─────────────────────────────────


class TestNetworkError:
    def test_default_message(self):
        err = OneBrainNetworkError()
        assert err.message == "Network connection failed"

    def test_custom_message(self):
        err = OneBrainNetworkError("DNS resolution failed")
        assert err.message == "DNS resolution failed"

    def test_default_status_code_is_none(self):
        err = OneBrainNetworkError()
        assert err.status_code is None


# ── OneBrainValidationError ──────────────────────────────


class TestValidationError:
    def test_default_message(self):
        err = OneBrainValidationError()
        assert err.message == "Validation error"

    def test_custom_message(self):
        err = OneBrainValidationError("Field 'title' is required")
        assert err.message == "Field 'title' is required"

    def test_default_status_code_is_none(self):
        err = OneBrainValidationError()
        assert err.status_code is None

    def test_status_code_passthrough(self):
        err = OneBrainValidationError(status_code=422)
        assert err.status_code == 422

    def test_kwargs_forwarded(self):
        err = OneBrainValidationError(
            "bad input",
            code="VALIDATION_ERROR",
            details=[{"field": "title", "error": "required"}],
        )
        assert err.code == "VALIDATION_ERROR"
        assert err.details == [{"field": "title", "error": "required"}]
