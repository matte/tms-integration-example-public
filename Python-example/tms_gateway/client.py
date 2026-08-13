"""A thin, typed-ish HTTP client for the Engaged Technologies TMS Gateway API."""

import json
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Union

import requests

from .auth import (
    DEFAULT_CLIENT_ID,
    DEFAULT_REDIRECT_URI,
    HeadlessPkceAuthenticator,
    PkceAuthenticator,
)
from .environments import DEFAULT_ENVIRONMENT, Environment, get_environment
from .exceptions import ApiError, NotFoundError, ValidationError

JsonDict = Dict[str, Any]

DEFAULT_TIMEOUT_SECONDS = 120


class Authenticator(Protocol):
    """Anything that can hand out a bearer token and be told to forget it."""

    def get_access_token(self) -> str:
        ...

    def invalidate(self) -> None:
        ...


class TmsGatewayClient:
    """Client for the TMS Gateway.

    Example:
        >>> client = TmsGatewayClient.for_environment("staging")
        >>> shipment = client.create_shipment({"accountNumber": "..."})
        >>> quote = client.quote_shipment(shipment["shipmentId"])
        >>> client.book_shipment(shipment["shipmentId"], {"selectedRateId": quote["rates"][0]["id"]})
    """

    def __init__(
        self,
        authenticator: Authenticator,
        environment: Environment = DEFAULT_ENVIRONMENT,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.authenticator = authenticator
        self.environment = environment
        self.timeout = timeout
        self.session = session or requests.Session()

    @classmethod
    def for_environment(
        cls,
        environment: Union[str, Environment] = DEFAULT_ENVIRONMENT,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = DEFAULT_CLIENT_ID,
        redirect_uri: str = DEFAULT_REDIRECT_URI,
        scopes: Optional[List[str]] = None,
        open_browser: bool = True,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> "TmsGatewayClient":
        """Build a client that authenticates with PKCE against the given environment.

        With ``username``/``password`` the headless flow is used: the
        authorization code is read from the ``Location`` header of the authorize
        response. Without them the browser flow with a loopback redirect is used.
        """
        env = get_environment(environment) if isinstance(environment, str) else environment
        authenticator: Authenticator
        if username and password:
            authenticator = HeadlessPkceAuthenticator(
                username=username,
                password=password,
                environment=env,
                client_id=client_id,
                redirect_uri=redirect_uri,
                scopes=scopes,
            )
        else:
            authenticator = PkceAuthenticator(
                environment=env,
                client_id=client_id,
                redirect_uri=redirect_uri,
                scopes=scopes,
                open_browser=open_browser,
            )
        return cls(authenticator=authenticator, environment=env, timeout=timeout)

    @property
    def base_url(self) -> str:
        return self.environment.gateway_base_url.rstrip("/")

    def login(self) -> None:
        """Force the token to be acquired now rather than on the first API call."""
        self.authenticator.get_access_token()

    # ------------------------------------------------------------------
    # Shipments
    # ------------------------------------------------------------------
    def create_shipment(self, shipment: JsonDict) -> JsonDict:
        """POST /shipments - create a shipment (BUILDING, REQUESTED or BOOKED)."""
        return self._request("POST", "/shipments", json_body=shipment)

    def get_shipment(self, shipment_id: str) -> JsonDict:
        """GET /shipments/{id}."""
        return self._request("GET", f"/shipments/{shipment_id}")

    def update_shipment(self, shipment: JsonDict) -> JsonDict:
        """PUT /shipments - the body must carry the shipment ``id``."""
        return self._request("PUT", "/shipments", json_body=shipment)

    def cancel_shipment(self, shipment_id: str) -> JsonDict:
        """DELETE /shipments/{id}."""
        return self._request("DELETE", f"/shipments/{shipment_id}")

    def list_shipments(
        self,
        name: Optional[str] = None,
        bill_number: Optional[str] = None,
        pro_number: Optional[str] = None,
        organization_id: Optional[str] = None,
        shipment_statuses: Optional[Sequence[str]] = None,
        created_start: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> JsonDict:
        """GET /shipments.

        The gateway requires at least one of ``name``, ``bill_number``,
        ``pro_number`` or ``organization_id``.
        """
        if not any([name, bill_number, pro_number, organization_id]):
            raise ValueError(
                "GET /shipments needs at least one of name, bill number, pro number or organization id."
            )

        params: List[tuple] = []
        for key, value in (
            ("name", name),
            ("billNumber", bill_number),
            ("proNumber", pro_number),
            ("organizationId", organization_id),
            ("createdStart", created_start),
            ("page", page),
            ("pageSize", page_size),
        ):
            if value is not None:
                params.append((key, value))
        for status in shipment_statuses or []:
            params.append(("shipmentStatuses", status))
        return self._request("GET", "/shipments", params=params)

    def search_shipments(
        self,
        query: Optional[str] = None,
        shipment_status: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> JsonDict:
        """GET /shipments/search - reference number search; ``query`` is required."""
        if not query:
            raise ValidationError("GET /shipments/search needs a reference number to search for.")
        params = {"q": query, "shipmentStatus": shipment_status, "page": page, "pageSize": page_size}
        return self._request("GET", "/shipments/search", params=_drop_none(params))

    def get_shipment_documents(self, shipment_id: str) -> JsonDict:
        """GET /shipments/{id}/documents."""
        return self._request("GET", f"/shipments/{shipment_id}/documents")

    # ------------------------------------------------------------------
    # Reference numbers
    # ------------------------------------------------------------------
    def add_reference_number(self, shipment_id: str, type: str, value: str) -> JsonDict:
        """POST /shipments/{id}/referenceNumbers."""
        return self._request(
            "POST",
            f"/shipments/{shipment_id}/referenceNumbers",
            json_body={"type": type, "value": value},
        )

    def delete_reference_number(self, shipment_id: str, reference_number_id: str) -> JsonDict:
        """DELETE /shipments/{id}/referenceNumbers/{referenceNumberId}."""
        return self._request(
            "DELETE", f"/shipments/{shipment_id}/referenceNumbers/{reference_number_id}"
        )

    def get_reference_numbers(self, shipment_id: str) -> List[JsonDict]:
        """Convenience helper: the reference numbers currently on a shipment."""
        shipment = self.get_shipment(shipment_id)
        return list(shipment.get("referenceNumbers") or [])

    # ------------------------------------------------------------------
    # Quoting and booking
    # ------------------------------------------------------------------
    def quote_shipment(self, shipment_id: str) -> JsonDict:
        """POST /shipments/{id}/quotes - rate an existing (BUILDING) shipment."""
        return self._request("POST", f"/shipments/{shipment_id}/quotes")

    def quick_quote(
        self, request: JsonDict, api_version: Optional[Union[str, int]] = None
    ) -> JsonDict:
        """POST /quotes - rate without creating a shipment.

        Version 1 takes a single ``totalWeight`` + ``freightClass``; version 2
        takes a ``units`` collection and is the one to use when dimensions are
        known. When ``api_version`` is omitted it is inferred from the body.
        """
        version = str(api_version) if api_version else ("2" if "units" in request else "1")
        return self._request("POST", "/quotes", json_body=request, api_version=version)

    def book_shipment(self, shipment_id: str, booking_options: JsonDict) -> JsonDict:
        """POST /shipments/{id}/bookingOptions - book against a selected rate."""
        return self._request(
            "POST", f"/shipments/{shipment_id}/bookingOptions", json_body=booking_options
        )

    # ------------------------------------------------------------------
    # Tracking
    # ------------------------------------------------------------------
    def track(
        self,
        pro_numbers: Optional[Iterable[str]] = None,
        bill_numbers: Optional[Iterable[str]] = None,
        shipment_ids: Optional[Iterable[str]] = None,
    ) -> List[JsonDict]:
        """GET /trackings - latest tracking status per matching shipment."""
        params: List[tuple] = []
        for value in pro_numbers or []:
            params.append(("proNumber", value))
        for value in bill_numbers or []:
            params.append(("billNumber", value))
        for value in shipment_ids or []:
            params.append(("shipmentId", value))
        if not params:
            raise ValueError("Provide at least one pro number, bill number or shipment id.")
        result = self._request("GET", "/trackings", params=params)
        if isinstance(result, dict):
            return list(result.get("items") or result.get("shipments") or [result])
        return list(result or [])

    def get_shipment_tracking(self, shipment_id: str) -> JsonDict:
        """GET /shipments/{id}/trackings - full tracking detail for one shipment."""
        return self._request("GET", f"/shipments/{shipment_id}/trackings")

    # ------------------------------------------------------------------
    # Reference data
    # ------------------------------------------------------------------
    def get_carriers(self, page: Optional[int] = None, page_size: Optional[int] = None) -> JsonDict:
        """GET /carriers."""
        return self._request("GET", "/carriers", params=_drop_none({"page": page, "pageSize": page_size}))

    def get_organizations(self) -> JsonDict:
        """GET /organizations."""
        return self._request("GET", "/organizations")

    # ------------------------------------------------------------------
    # Plumbing
    # ------------------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[JsonDict] = None,
        params: Optional[Any] = None,
        api_version: str = "1",
        _retrying: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.authenticator.get_access_token()}",
            "Accept": "application/json",
            "x-api-version": str(api_version),
        }
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        response = self.session.request(
            method,
            url,
            headers=headers,
            json=json_body,
            params=params,
            timeout=self.timeout,
        )

        # An expired or revoked token means we re-authenticate once and retry.
        if response.status_code == 401 and not _retrying:
            self.authenticator.invalidate()
            return self._request(
                method, path, json_body=json_body, params=params, api_version=api_version, _retrying=True
            )

        if response.status_code >= 400:
            raise _error_for(response, method, url)

        if response.status_code == 204 or not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}


def _drop_none(values: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def _error_for(response: requests.Response, method: str, url: str) -> ApiError:
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text

    kwargs = {
        "status_code": response.status_code,
        "method": method,
        "url": url,
        "body": body,
        "error_type": response.headers.get("tms-error-type"),
        "location_code": response.headers.get("tms-error-location-code"),
    }
    if response.status_code == 404:
        return NotFoundError(**kwargs)
    if response.status_code in (400, 422):
        return ValidationError(**kwargs)
    return ApiError(**kwargs)


def pretty(payload: Any) -> str:
    """Format an API payload for display."""
    return json.dumps(payload, indent=2, sort_keys=False, default=str)
