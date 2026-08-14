"""Exceptions raised by the TMS Gateway client."""

from typing import Any, Optional


class TmsGatewayError(Exception):
    """Base error for every failure surfaced by this package."""


class AuthenticationError(TmsGatewayError):
    """Raised when the PKCE authorization flow cannot produce an access token."""


class ApiError(TmsGatewayError):
    """Raised when the gateway returns a non-success HTTP status code.

    The gateway returns RFC7807 problem details plus the ``tms-error-type`` and
    ``tms-error-location-code`` headers, all of which are captured here.
    """

    def __init__(
        self,
        status_code: int,
        method: str,
        url: str,
        body: Any = None,
        error_type: Optional[str] = None,
        location_code: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.method = method
        self.url = url
        self.body = body
        self.error_type = error_type
        self.location_code = location_code
        super().__init__(self._describe())

    def _describe(self) -> str:
        parts = [f"{self.method} {self.url} failed with HTTP {self.status_code}"]
        if self.error_type:
            parts.append(f"type={self.error_type}")
        if self.location_code:
            parts.append(f"locationCode={self.location_code}")
        detail = self.detail
        if detail:
            parts.append(detail)
        return " | ".join(parts)

    @property
    def detail(self) -> str:
        """A human readable message pulled out of the problem details body."""
        body = self.body
        if isinstance(body, dict):
            for key in ("detail", "title", "message", "displayMessage"):
                value = body.get(key)
                if value:
                    return str(value)
            errors = body.get("errors")
            if isinstance(errors, dict):
                return "; ".join(
                    f"{field}: {', '.join(str(m) for m in messages)}"
                    if isinstance(messages, list)
                    else f"{field}: {messages}"
                    for field, messages in errors.items()
                )
        if isinstance(body, str):
            return body.strip()
        return ""


class NotFoundError(ApiError):
    """Raised when the gateway returns HTTP 404."""


class ValidationError(ApiError):
    """Raised when the gateway rejects the request body (HTTP 400/422)."""
