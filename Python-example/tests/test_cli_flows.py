"""Drives the console flows end to end with scripted keystrokes and a fake gateway."""

import io
from typing import Any, Dict, List

import pytest

from tms_cli import quotes, shipments, tracking


class FakeClient:
    """Stands in for TmsGatewayClient and records what the CLI asked for."""

    def __init__(self) -> None:
        self.calls: List[Any] = []
        self.shipment: Dict[str, Any] = {
            "shipmentId": "11111111-1111-1111-1111-111111111111",
            "name": "SHIP-1",
            "shipmentStatus": "BUILDING",
            "mode": "LTL",
            "equipmentType": "LTL_DRY_VAN",
            "serviceLevel": "STANDARD",
            "units": [],
            "referenceNumbers": [{"id": "ref-1", "type": "PO_NUMBER", "value": "PO-1"}],
        }
        self.quote = {
            "quoteNumber": "Q-1",
            "distance": 510,
            "rates": [
                {
                    "id": "rate-1",
                    "carrierName": "Cheap Freight",
                    "carrierId": "carrier-1",
                    "displayScac": "CHEP",
                    "mode": "LTL",
                    "serviceLevel": "STANDARD",
                    "serviceDays": 3,
                    "totalCharge": 250.5,
                    "currencyType": "USD",
                },
                {
                    "id": "rate-2",
                    "carrierName": "Fast Freight",
                    "carrierId": "carrier-2",
                    "displayScac": "FAST",
                    "mode": "LTL",
                    "serviceLevel": "GUARANTEED",
                    "serviceDays": 1,
                    "totalCharge": 480.0,
                    "currencyType": "USD",
                },
            ],
            "alternateOptions": [{"optionType": "TRUCKLOAD", "description": "Submit as requested"}],
        }

    def create_shipment(self, body):
        self.calls.append(("create_shipment", body))
        return dict(self.shipment)

    def get_shipment(self, shipment_id):
        return dict(self.shipment)

    def update_shipment(self, body):
        self.calls.append(("update_shipment", body))
        return dict(self.shipment)

    def quote_shipment(self, shipment_id):
        self.calls.append(("quote_shipment", shipment_id))
        return self.quote

    def quick_quote(self, body, api_version=None):
        self.calls.append(("quick_quote", body, api_version))
        return self.quote

    def book_shipment(self, shipment_id, booking_options):
        self.calls.append(("book_shipment", shipment_id, booking_options))
        return {
            "shipmentStatus": "BOOKED",
            "carrierName": "Fast Freight",
            "billNumber": "BOL-9",
            "trackingNumber": "PRO-9",
        }

    def get_reference_numbers(self, shipment_id):
        return list(self.shipment["referenceNumbers"])

    def add_reference_number(self, shipment_id, type, value):
        self.calls.append(("add_reference_number", shipment_id, type, value))
        return {"id": "ref-2", "type": type, "value": value}

    def delete_reference_number(self, shipment_id, reference_number_id):
        self.calls.append(("delete_reference_number", shipment_id, reference_number_id))
        return {}

    def track(self, pro_numbers=None, bill_numbers=None, shipment_ids=None):
        self.calls.append(("track", list(pro_numbers or []), list(bill_numbers or []), list(shipment_ids or [])))
        return [
            {
                "shipmentId": "11111111-1111-1111-1111-111111111111",
                "billNumber": "BOL-9",
                "proNumber": "PRO-9",
                "carrierName": "Fast Freight",
                "trackingStatus": "IN_TRANSIT",
                "dateTime": "2026-08-04T10:00:00",
                "city": "Kansas City",
                "stateCode": "MO",
            }
        ]

    def get_shipment_tracking(self, shipment_id):
        self.calls.append(("get_shipment_tracking", shipment_id))
        return {
            "billNumber": "BOL-9",
            "carrierName": "Fast Freight",
            "proNumber": "PRO-9",
            "stops": [{"sequenceNumber": 1, "city": "Kansas City", "stateCode": "MO", "stopStatus": "DEPARTED"}],
            "trackingEvents": [{"dateTime": "2026-08-04T10:00:00", "status": "IN_TRANSIT", "description": "Departed"}],
        }


@pytest.fixture
def keystrokes(monkeypatch):
    """Feed scripted answers to every prompt the flow asks for."""

    def feed(answers: List[str]) -> None:
        monkeypatch.setattr("sys.stdin", io.StringIO("\n".join(answers) + "\n"))

    return feed


def test_guided_quick_quote_without_dimensions_uses_version_one(keystrokes):
    client = FakeClient()
    keystrokes(
        [
            "1",        # enter values step by step
            "64102",    # origin postal code
            "US",       # origin country
            "60661",    # destination postal code
            "US",       # destination country
            "",         # organization id
            "n",        # no dimensions
            "",         # origin accessorials
            "5",        # destination accessorials -> LIFTGATE
            "",         # product accessorials
            "",         # shipment accessorials
            "850",      # total weight
            "9",        # freight class -> FREIGHT_CLASS_100
            "y",        # send it
        ]
    )

    quotes.quick_quote_flow(client)

    name, body, version = client.calls[0]
    assert name == "quick_quote"
    assert version == "1"
    assert body["totalWeight"] == 850
    assert body["freightClass"] == "FREIGHT_CLASS_100"
    assert body["destinationAccessorials"] == ["LIFTGATE"]
    assert "units" not in body


def test_guided_quick_quote_with_dimensions_uses_version_two(keystrokes):
    client = FakeClient()
    keystrokes(
        [
            "1",        # enter values step by step
            "64102", "US", "60661", "US",
            "",         # organization id
            "y",        # has dimensions
            "", "", "", "",   # accessorials
            "",         # origin location type
            "",         # destination location type
            "1",        # equipment type -> LTL_DRY_VAN
            "2",        # quantity
            "1",        # package type -> PALLETS
            "850",      # total weight
            "48", "40", "45",  # dims
            "9",        # freight class
            "Valves",   # description
            "n",        # hazmat
            "n",        # no more units
            "y",        # send it
        ]
    )

    quotes.quick_quote_flow(client)

    name, body, version = client.calls[0]
    assert name == "quick_quote"
    assert version == "2"
    assert body["units"][0]["length"] == 48
    assert body["units"][0]["freightClass"] == "FREIGHT_CLASS_100"
    assert body["equipmentType"] == "LTL_DRY_VAN"


def test_create_shipment_then_quote_and_book(keystrokes):
    client = FakeClient()
    keystrokes(
        [
            "1",            # enter values step by step
            "ACCT-1",       # account number
            "1",            # mode LTL
            "1",            # equipment LTL_DRY_VAN
            "1",            # service level STANDARD
            "1",            # status BUILDING
            "2026-08-10",   # pickup date
            "",             # delivery date
            # origin stop (blanks: address2, direction type, contacts, dates/times, instructions)
            "Warehouse", "1600 Genessee St", "Kansas City", "MO", "64102", "US",
            "", "", "", "", "", "", "", "", "", "",
            "",             # no origin accessorials
            # destination stop
            "Acme", "500 W Madison St", "Chicago", "IL", "60661", "US",
            "", "", "", "", "", "", "", "", "", "",
            "5",            # destination accessorial -> LIFTGATE
            "n",            # no additional stop
            # unit 1
            "Valves", "2", "1", "850", "9", "n", "", "n",
            "n",            # no more units
            # BUILDING shipments need at least one reference number
            "1", "PO-100234",
            "n",            # no further reference numbers
            "n",            # no product/shipment accessorials
            "y",            # is complete
            "",             # carrier scac
            "y",            # send it
            # shipment menu -> quote
            "2",
            "y",            # select a rate and book
            "2",            # rate 2 (not the cheapest)
            "n",            # dispatch
            "3",            # reason CUSTOMER_SPECIFIED
            "Customer asked for the faster carrier",
            "y",            # book it
            "0",            # back to main menu
        ]
    )

    shipments.create_shipment_flow(client)

    created = next(call for call in client.calls if call[0] == "create_shipment")[1]
    assert created["accountNumber"] == "ACCT-1"
    assert len(created["stops"]) == 2
    assert created["stops"][1]["sequenceNumber"] == 2
    # origin/destination accessorials must ride on the stop, not on the shipment
    assert created["stops"][1]["accessorials"] == [
        {"accessorialCode": "LIFTGATE", "accessorialType": "DESTINATION"}
    ]
    assert "accessorials" not in created
    assert created["units"][0]["freightClass"] == "FREIGHT_CLASS_100"
    assert created["referenceNumbers"] == [{"type": "PO_NUMBER", "value": "PO-100234"}]

    booked = next(call for call in client.calls if call[0] == "book_shipment")
    assert booked[2]["selectedRateId"] == "rate-2"
    assert booked[2]["selectedReasonType"] == "CUSTOMER_SPECIFIED"


def test_reference_numbers_can_be_added_and_deleted(keystrokes):
    client = FakeClient()
    keystrokes(
        [
            "1",            # add
            "2",            # SO_NUMBER
            "SO-100",
            "2",            # delete
            "1",            # the only reference number
            "y",            # confirm
            "0",            # back
        ]
    )

    shipments.reference_number_menu(client, "ship-1")

    assert ("add_reference_number", "ship-1", "SO_NUMBER", "SO-100") in client.calls
    assert ("delete_reference_number", "ship-1", "ref-1") in client.calls


def test_tracking_by_pro_number_then_detail(keystrokes):
    client = FakeClient()
    keystrokes(["1", "PRO-9, PRO-10", "y", "1"])

    tracking.track_flow(client)

    assert ("track", ["PRO-9", "PRO-10"], [], []) in client.calls
    assert ("get_shipment_tracking", "11111111-1111-1111-1111-111111111111") in client.calls
