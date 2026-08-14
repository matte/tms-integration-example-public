"""Offline tests for the client: nothing here touches a real environment."""

import json
from typing import Any, Dict, List, Optional

import pytest

from tms_gateway import StaticTokenAuthenticator, TmsGatewayClient, get_environment
from tms_gateway.exceptions import ApiError, NotFoundError, ValidationError


class FakeResponse:
    def __init__(self, status_code: int, payload: Any = None, headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self.content = b"" if payload is None else json.dumps(payload).encode()
        self.text = "" if payload is None else json.dumps(payload)

    def json(self) -> Any:
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeSession:
    """Records requests and replays queued responses."""

    def __init__(self, responses: List[FakeResponse]):
        self.responses = list(responses)
        self.calls: List[Dict[str, Any]] = []

    def request(self, method, url, headers=None, json=None, params=None, timeout=None):
        self.calls.append(
            {"method": method, "url": url, "headers": headers, "json": json, "params": params}
        )
        return self.responses.pop(0)


def build_client(responses: List[FakeResponse]) -> TmsGatewayClient:
    return TmsGatewayClient(
        authenticator=StaticTokenAuthenticator("token-abc"),
        environment=get_environment("qa"),
        session=FakeSession(responses),
    )


def test_create_shipment_posts_body_with_bearer_token():
    client = build_client([FakeResponse(201, {"shipmentId": "abc", "shipmentStatus": "BUILDING"})])

    shipment = client.create_shipment({"accountNumber": "123"})

    call = client.session.calls[0]
    assert shipment["shipmentId"] == "abc"
    assert call["method"] == "POST"
    assert call["url"] == "https://tmsgateway-qa.engagedtechnologies.com/shipments"
    assert call["json"] == {"accountNumber": "123"}
    assert call["headers"]["Authorization"] == "Bearer token-abc"
    assert call["headers"]["x-api-version"] == "1"


def test_quick_quote_uses_version_two_when_units_are_present():
    client = build_client([FakeResponse(201, {"rates": []})])

    client.quick_quote({"originPostalCode": "64102", "units": [{"totalWeight": 100}]})

    assert client.session.calls[0]["headers"]["x-api-version"] == "2"


def test_quick_quote_uses_version_one_without_units():
    client = build_client([FakeResponse(201, {"rates": []})])

    client.quick_quote({"originPostalCode": "64102", "totalWeight": 100})

    assert client.session.calls[0]["headers"]["x-api-version"] == "1"


def test_track_sends_repeated_query_parameters():
    client = build_client([FakeResponse(200, [{"shipmentId": "abc"}])])

    results = client.track(pro_numbers=["111", "222"], bill_numbers=["333"])

    assert results == [{"shipmentId": "abc"}]
    assert client.session.calls[0]["params"] == [
        ("proNumber", "111"),
        ("proNumber", "222"),
        ("billNumber", "333"),
    ]


def test_track_requires_at_least_one_identifier():
    client = build_client([])

    with pytest.raises(ValueError):
        client.track()


def test_delete_reference_number_returns_empty_body_for_204():
    client = build_client([FakeResponse(204)])

    assert client.delete_reference_number("ship-1", "ref-1") == {}
    assert client.session.calls[0]["method"] == "DELETE"
    assert client.session.calls[0]["url"].endswith("/shipments/ship-1/referenceNumbers/ref-1")


def test_expired_token_triggers_one_reauthentication_and_retry():
    class RecordingAuthenticator(StaticTokenAuthenticator):
        def __init__(self):
            super().__init__("token-abc")
            self.invalidations = 0

        def invalidate(self):
            self.invalidations += 1

    authenticator = RecordingAuthenticator()
    session = FakeSession([FakeResponse(401, {"title": "expired"}), FakeResponse(200, {"shipmentId": "abc"})])
    client = TmsGatewayClient(authenticator, get_environment("qa"), session=session)

    assert client.get_shipment("abc")["shipmentId"] == "abc"
    assert authenticator.invalidations == 1
    assert len(session.calls) == 2


def test_persistent_401_is_raised_as_api_error():
    session = FakeSession([FakeResponse(401, {"title": "nope"}), FakeResponse(401, {"title": "nope"})])
    client = TmsGatewayClient(StaticTokenAuthenticator("t"), get_environment("qa"), session=session)

    with pytest.raises(ApiError) as raised:
        client.get_shipment("abc")

    assert raised.value.status_code == 401


def test_validation_error_exposes_tms_headers_and_detail():
    client = build_client(
        [
            FakeResponse(
                400,
                {"title": "Invalid request", "errors": {"accountNumber": ["must not be empty"]}},
                {"tms-error-type": "VALIDATION_ERROR", "tms-error-location-code": "MXZ8SQ1"},
            )
        ]
    )

    with pytest.raises(ValidationError) as raised:
        client.create_shipment({})

    error = raised.value
    assert error.error_type == "VALIDATION_ERROR"
    assert error.location_code == "MXZ8SQ1"
    assert "Invalid request" in error.detail


def test_missing_shipment_raises_not_found():
    client = build_client([FakeResponse(404, {"title": "Shipment not found"})])

    with pytest.raises(NotFoundError):
        client.get_shipment("missing")


def test_search_shipments_drops_empty_parameters():
    client = build_client([FakeResponse(200, {"items": []})])

    client.search_shipments(query="PO-1")

    assert client.session.calls[0]["params"] == {"q": "PO-1"}
