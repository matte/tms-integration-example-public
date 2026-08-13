"""OAuth2 authorization code + PKCE authentication against the TMS identity server.

Two authenticators are provided, both doing a full PKCE exchange:

* :class:`HeadlessPkceAuthenticator` signs in with the user's credentials and
  reads the authorization code out of the ``Location`` header of the authorize
  response, exactly like the Postman collection. No browser, no local listener.
* :class:`PkceAuthenticator` opens the identity server in a browser and captures
  the code on a loopback redirect uri.

Tokens are held in memory only. The ``Sandbox`` client issues no refresh token,
so an expired token is renewed by simply repeating the flow.
"""

import base64
import hashlib
import http.server
import secrets
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import requests

from .environments import DEFAULT_ENVIRONMENT, Environment
from .exceptions import AuthenticationError

DEFAULT_CLIENT_ID = "Sandbox"

# Must exactly match a redirect uri registered for the client in the identity
# server. Nothing listens on it during the headless flow - the identity server
# only needs it to build the redirect it hands back in the Location header.
DEFAULT_REDIRECT_URI = "http://localhost:5555/auth"

DEFAULT_SCOPES = (
    "openid",
    "profile",
    "gatewayShipments",
    "gatewayRates",
    "gatewayTrackings",
)

# Renew this many seconds before the token actually expires.
EXPIRY_SKEW_SECONDS = 60


@dataclass
class Token:
    """An access token and the moment it stops being usable."""

    access_token: str
    token_type: str
    expires_at: float
    id_token: Optional[str] = None
    scope: Optional[str] = None

    @property
    def seconds_remaining(self) -> float:
        return max(0.0, self.expires_at - time.time())

    def is_expired(self, skew: float = EXPIRY_SKEW_SECONDS) -> bool:
        return time.time() >= (self.expires_at - skew)


class BasePkceAuthenticator:
    """Shared PKCE plumbing: discovery, authorize url, code exchange, caching."""

    def __init__(
        self,
        environment: Environment = DEFAULT_ENVIRONMENT,
        client_id: str = DEFAULT_CLIENT_ID,
        redirect_uri: str = DEFAULT_REDIRECT_URI,
        scopes: Optional[List[str]] = None,
    ) -> None:
        self.environment = environment
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = list(scopes) if scopes else list(DEFAULT_SCOPES)
        self._token: Optional[Token] = None
        self._endpoints: Optional[Dict[str, str]] = None
        self._lock = threading.Lock()

    @property
    def token(self) -> Optional[Token]:
        """The token currently held in memory, if any."""
        return self._token

    def get_access_token(self) -> str:
        """Return a valid access token, re-authenticating when it has expired."""
        with self._lock:
            if self._token is None or self._token.is_expired():
                self._token = self._authorize()
            return self._token.access_token

    def invalidate(self) -> None:
        """Drop the cached token so the next call re-authenticates."""
        with self._lock:
            self._token = None

    def logout(self) -> None:
        self.invalidate()

    def discover(self) -> Dict[str, str]:
        """Resolve the authorize/token endpoints from OpenID discovery."""
        if self._endpoints is not None:
            return self._endpoints

        base = self.environment.identity_base_url.rstrip("/")
        fallback = {
            "authorization_endpoint": f"{base}/connect/authorize",
            "token_endpoint": f"{base}/connect/token",
            "end_session_endpoint": f"{base}/connect/endsession",
        }
        try:
            response = requests.get(f"{base}/.well-known/openid-configuration", timeout=30)
            response.raise_for_status()
            document = response.json()
            self._endpoints = {
                key: document.get(key, fallback.get(key, ""))
                for key in ("authorization_endpoint", "token_endpoint", "end_session_endpoint")
            }
        except (requests.RequestException, ValueError):
            self._endpoints = fallback
        return self._endpoints

    def _authorize(self) -> Token:
        raise NotImplementedError

    def _new_pkce_pair(self) -> tuple:
        verifier = _generate_code_verifier()
        return verifier, _code_challenge_for(verifier)

    def _authorize_params(self, code_challenge: str, state: str) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

    def _authorize_url(self, code_challenge: str, state: str) -> str:
        params = self._authorize_params(code_challenge, state)
        params["nonce"] = secrets.token_urlsafe(24)
        return self.discover()["authorization_endpoint"] + "?" + urllib.parse.urlencode(params)

    def _code_from_query(self, query: Dict[str, str], expected_state: str) -> str:
        if query.get("state") != expected_state:
            raise AuthenticationError("The identity server returned a mismatched state value.")
        if "error" in query:
            description = query.get("error_description", "")
            raise AuthenticationError(f"Authorization failed: {query['error']} {description}".strip())
        code = query.get("code")
        if not code:
            raise AuthenticationError("The identity server did not return an authorization code.")
        return code

    def _exchange_code(
        self, code: str, code_verifier: str, session: Optional[requests.Session] = None
    ) -> Token:
        poster = session.post if session else requests.post
        response = poster(
            self.discover()["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "code": code,
                "redirect_uri": self.redirect_uri,
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=60,
        )
        if response.status_code >= 400:
            raise AuthenticationError(
                f"Token endpoint returned HTTP {response.status_code}: {response.text.strip()}"
            )

        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise AuthenticationError(f"Token endpoint response contained no access token: {payload}")

        return Token(
            access_token=access_token,
            token_type=payload.get("token_type", "Bearer"),
            expires_at=time.time() + float(payload.get("expires_in", 3600)),
            id_token=payload.get("id_token"),
            scope=payload.get("scope"),
        )


class HeadlessPkceAuthenticator(BasePkceAuthenticator):
    """PKCE without a browser.

    Posts the credentials to ``/api/account/login`` for the identity cookie,
    calls ``/connect/authorize`` without following redirects and takes the
    authorization code from the ``Location`` response header, then exchanges it
    for a token. The credentials stay in memory so an expired token is renewed
    without any user interaction.
    """

    def __init__(
        self,
        username: str,
        password: str,
        environment: Environment = DEFAULT_ENVIRONMENT,
        client_id: str = DEFAULT_CLIENT_ID,
        redirect_uri: str = DEFAULT_REDIRECT_URI,
        scopes: Optional[List[str]] = None,
    ) -> None:
        super().__init__(environment=environment, client_id=client_id, redirect_uri=redirect_uri, scopes=scopes)
        self.username = username
        self.password = password

    @property
    def login_url(self) -> str:
        return self.environment.identity_base_url.rstrip("/") + "/api/account/login"

    def _authorize(self) -> Token:
        session = requests.Session()
        self._sign_in(session)

        code_verifier, code_challenge = self._new_pkce_pair()
        state = secrets.token_urlsafe(24)

        response = session.post(
            self.discover()["authorization_endpoint"],
            data=self._authorize_params(code_challenge, state),
            allow_redirects=False,
            timeout=60,
        )

        location = response.headers.get("Location", "")
        if response.status_code not in (301, 302, 303, 307, 308) or not location:
            raise AuthenticationError(
                "The authorize endpoint did not redirect with an authorization code "
                f"(HTTP {response.status_code}). The account may need to consent, or the "
                "client may not allow this redirect uri."
            )

        query = {key: values[0] for key, values in urllib.parse.parse_qs(urllib.parse.urlparse(location).query).items()}
        code = self._code_from_query(query, state)
        return self._exchange_code(code, code_verifier, session=session)

    def _sign_in(self, session: requests.Session) -> None:
        response = session.post(
            self.login_url,
            json={"email": self.username, "password": self.password, "rememberMe": False},
            timeout=60,
        )
        if response.status_code >= 400:
            raise AuthenticationError(
                f"Sign in failed for {self.username} (HTTP {response.status_code}). "
                "Check the username and password for this environment."
            )


class PkceAuthenticator(BasePkceAuthenticator):
    """PKCE through the browser, capturing the code on a loopback redirect uri."""

    def __init__(
        self,
        environment: Environment = DEFAULT_ENVIRONMENT,
        client_id: str = DEFAULT_CLIENT_ID,
        redirect_uri: str = DEFAULT_REDIRECT_URI,
        scopes: Optional[List[str]] = None,
        timeout_seconds: int = 300,
        open_browser: bool = True,
        prompt_url: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(environment=environment, client_id=client_id, redirect_uri=redirect_uri, scopes=scopes)
        self.timeout_seconds = timeout_seconds
        self.open_browser = open_browser
        self.prompt_url = prompt_url

    def _authorize(self) -> Token:
        code_verifier, code_challenge = self._new_pkce_pair()
        state = secrets.token_urlsafe(24)

        query = self._await_callback(self._authorize_url(code_challenge, state))
        code = self._code_from_query(query, state)
        return self._exchange_code(code, code_verifier)

    def _await_callback(self, authorize_url: str) -> Dict[str, str]:
        parsed_redirect = urllib.parse.urlparse(self.redirect_uri)
        host = parsed_redirect.hostname or "localhost"
        port = parsed_redirect.port or 80

        handler = type(
            "_ScopedCallbackHandler",
            (_CallbackHandler,),
            {"result": {}, "callback_path": parsed_redirect.path or "/"},
        )

        try:
            server = http.server.HTTPServer((host, port), handler)
        except OSError as error:
            raise AuthenticationError(
                f"Could not listen on {host}:{port} for the PKCE redirect ({error}). "
                "Free the port or configure a different registered redirect uri."
            ) from error

        server.timeout = self.timeout_seconds
        try:
            if self.prompt_url:
                self.prompt_url(authorize_url)
            if self.open_browser:
                webbrowser.open(authorize_url)
            server.handle_request()
        finally:
            server.server_close()

        if not handler.result:
            raise AuthenticationError(
                f"Timed out after {self.timeout_seconds}s waiting for the identity server redirect."
            )
        return dict(handler.result)


class StaticTokenAuthenticator:
    """Uses a pre-issued access token; handy for scripts and automated tests."""

    def __init__(self, access_token: str, expires_in: float = 8 * 60 * 60) -> None:
        self._token = Token(
            access_token=access_token,
            token_type="Bearer",
            expires_at=time.time() + expires_in,
        )

    @property
    def token(self) -> Token:
        return self._token

    def get_access_token(self) -> str:
        return self._token.access_token

    def invalidate(self) -> None:
        """No-op: a static token cannot be renewed."""


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """Single-shot handler that captures the authorization code off the redirect."""

    result: Dict[str, str] = {}
    callback_path = "/auth"

    def do_GET(self) -> None:  # noqa: N802 - name required by BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != self.callback_path:
            self.send_response(404)
            self.end_headers()
            return

        query = {key: values[0] for key, values in urllib.parse.parse_qs(parsed.query).items()}
        type(self).result.update(query)

        succeeded = "code" in query
        message = (
            "Authentication complete. You can close this tab and return to the terminal."
            if succeeded
            else f"Authentication failed: {query.get('error', 'no authorization code returned')}"
        )
        body = (
            "<html><head><title>TMS Gateway</title></head>"
            f"<body style=\"font-family: sans-serif; padding: 2rem;\"><h3>{message}</h3></body></html>"
        ).encode("utf-8")

        self.send_response(200 if succeeded else 400)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - signature is fixed
        """Silence the default stderr request logging."""


def _generate_code_verifier() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("ascii").rstrip("=")


def _code_challenge_for(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
