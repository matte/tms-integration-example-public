"""Offline tests for the PKCE helpers and token lifetime handling."""

import base64
import hashlib
import time
import urllib.parse

import pytest

from tms_gateway.auth import (
    PkceAuthenticator,
    Token,
    _code_challenge_for,
    _generate_code_verifier,
)
from tms_gateway.environments import get_environment


def test_code_challenge_is_url_safe_sha256_of_the_verifier():
    verifier = _generate_code_verifier()

    challenge = _code_challenge_for(verifier)

    expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    assert challenge == expected
    assert "=" not in challenge
    assert 43 <= len(verifier) <= 128


def test_token_reports_expiry_within_the_skew_window():
    assert Token("t", "Bearer", time.time() + 3600).is_expired() is False
    assert Token("t", "Bearer", time.time() + 30).is_expired() is True
    assert Token("t", "Bearer", time.time() - 1).is_expired() is True


def test_discovery_falls_back_to_the_conventional_endpoints(monkeypatch):
    authenticator = PkceAuthenticator(environment=get_environment("qa"))

    def explode(*args, **kwargs):
        raise __import__("requests").RequestException("no network")

    monkeypatch.setattr("tms_gateway.auth.requests.get", explode)

    endpoints = authenticator.discover()

    assert endpoints["authorization_endpoint"] == (
        "https://login.tms-qa.engagedtechnologies.com/connect/authorize"
    )
    assert endpoints["token_endpoint"] == "https://login.tms-qa.engagedtechnologies.com/connect/token"


def test_authorize_url_carries_pkce_parameters(monkeypatch):
    captured = {}

    authenticator = PkceAuthenticator(environment=get_environment("qa"), open_browser=False)
    monkeypatch.setattr(
        PkceAuthenticator,
        "discover",
        lambda self: {
            "authorization_endpoint": "https://login.example/connect/authorize",
            "token_endpoint": "https://login.example/connect/token",
        },
    )

    def fake_await_callback(self, authorize_url):
        captured["url"] = authorize_url
        query = urllib.parse.parse_qs(urllib.parse.urlparse(authorize_url).query)
        return {"code": "the-code", "state": query["state"][0]}

    def fake_exchange(self, code, code_verifier):
        captured["code"] = code
        captured["verifier"] = code_verifier
        return Token("access-token", "Bearer", time.time() + 3600)

    monkeypatch.setattr(PkceAuthenticator, "_await_callback", fake_await_callback)
    monkeypatch.setattr(PkceAuthenticator, "_exchange_code", fake_exchange)

    assert authenticator.get_access_token() == "access-token"

    query = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
    assert query["client_id"] == ["Sandbox"]
    assert query["redirect_uri"] == ["http://localhost:5555/auth"]
    assert query["response_type"] == ["code"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"] == [_code_challenge_for(captured["verifier"])]
    assert "gatewayShipments" in query["scope"][0]


def test_token_is_reused_until_it_expires(monkeypatch):
    authenticator = PkceAuthenticator(environment=get_environment("qa"), open_browser=False)
    calls = {"count": 0}

    def fake_authorize(self):
        calls["count"] += 1
        return Token(f"token-{calls['count']}", "Bearer", time.time() + 3600)

    monkeypatch.setattr(PkceAuthenticator, "_authorize", fake_authorize)

    assert authenticator.get_access_token() == "token-1"
    assert authenticator.get_access_token() == "token-1"

    authenticator.invalidate()
    assert authenticator.get_access_token() == "token-2"
    assert calls["count"] == 2


class _FakeResponse:
    def __init__(self, status_code, headers=None, payload=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._payload = payload or {}
        self.text = ""

    def json(self):
        return self._payload


class _FakeSession:
    """Records the login post and answers the authorize call with a 302."""

    def __init__(self, location, login_status=200):
        self.location = location
        self.login_status = login_status
        self.posts = []

    def post(self, url, json=None, data=None, headers=None, timeout=None, allow_redirects=None):
        self.posts.append({"url": url, "json": json, "data": data, "allow_redirects": allow_redirects})
        if url.endswith("/api/account/login"):
            return _FakeResponse(self.login_status)
        if url.endswith("/connect/authorize"):
            return _FakeResponse(302, headers={"Location": self.location(data["state"])})
        return _FakeResponse(
            200, payload={"access_token": "headless-token", "expires_in": 28800, "token_type": "Bearer"}
        )


def _headless(monkeypatch, session):
    from tms_gateway.auth import HeadlessPkceAuthenticator

    monkeypatch.setattr("tms_gateway.auth.requests.Session", lambda: session)
    authenticator = HeadlessPkceAuthenticator(
        username="user@example.com", password="secret", environment=get_environment("qa")
    )
    monkeypatch.setattr(
        type(authenticator),
        "discover",
        lambda self: {
            "authorization_endpoint": "https://login.tms-qa.engagedtechnologies.com/connect/authorize",
            "token_endpoint": "https://login.tms-qa.engagedtechnologies.com/connect/token",
        },
    )
    return authenticator


def test_headless_flow_reads_the_code_from_the_location_header(monkeypatch):
    session = _FakeSession(lambda state: f"http://localhost:5555/auth?code=THE-CODE&state={state}")
    authenticator = _headless(monkeypatch, session)

    assert authenticator.get_access_token() == "headless-token"

    login_post, authorize_post, token_post = session.posts
    assert login_post["url"].endswith("/api/account/login")
    assert login_post["json"] == {"email": "user@example.com", "password": "secret", "rememberMe": False}
    assert authorize_post["allow_redirects"] is False
    assert authorize_post["data"]["code_challenge_method"] == "S256"
    assert token_post["data"]["code"] == "THE-CODE"
    assert token_post["data"]["grant_type"] == "authorization_code"
    assert _code_challenge_for(token_post["data"]["code_verifier"]) == authorize_post["data"]["code_challenge"]


def test_headless_flow_rejects_a_mismatched_state(monkeypatch):
    from tms_gateway.exceptions import AuthenticationError

    session = _FakeSession(lambda state: "http://localhost:5555/auth?code=X&state=not-the-state")
    authenticator = _headless(monkeypatch, session)

    with pytest.raises(AuthenticationError):
        authenticator.get_access_token()


def test_headless_flow_reports_a_failed_sign_in(monkeypatch):
    from tms_gateway.exceptions import AuthenticationError

    session = _FakeSession(lambda state: "", login_status=401)
    authenticator = _headless(monkeypatch, session)

    with pytest.raises(AuthenticationError) as raised:
        authenticator.get_access_token()

    assert "Sign in failed" in str(raised.value)


def test_expired_token_is_renewed_automatically(monkeypatch):
    authenticator = PkceAuthenticator(environment=get_environment("qa"), open_browser=False)
    tokens = iter(
        [
            Token("expired-token", "Bearer", time.time() + 5),  # inside the 60s skew window
            Token("fresh-token", "Bearer", time.time() + 3600),
        ]
    )
    monkeypatch.setattr(PkceAuthenticator, "_authorize", lambda self: next(tokens))

    assert authenticator.get_access_token() == "expired-token"
    assert authenticator.get_access_token() == "fresh-token"
