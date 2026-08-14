"""Python client for the Engaged Technologies TMS Gateway API."""

from .auth import (
    HeadlessPkceAuthenticator,
    PkceAuthenticator,
    StaticTokenAuthenticator,
    Token,
)
from .client import TmsGatewayClient, pretty
from .environments import ENVIRONMENTS, PRODUCTION, QA, STAGING, Environment, get_environment
from .exceptions import ApiError, AuthenticationError, NotFoundError, TmsGatewayError, ValidationError

__all__ = [
    "ApiError",
    "AuthenticationError",
    "ENVIRONMENTS",
    "Environment",
    "HeadlessPkceAuthenticator",
    "NotFoundError",
    "PRODUCTION",
    "PkceAuthenticator",
    "QA",
    "STAGING",
    "StaticTokenAuthenticator",
    "TmsGatewayClient",
    "TmsGatewayError",
    "Token",
    "ValidationError",
    "get_environment",
    "pretty",
]

__version__ = "0.1.0"
