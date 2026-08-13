"""Minimal example of using the shared client without the interactive console."""

import getpass
import json
import os

from tms_gateway import TmsGatewayClient, pretty


def main() -> None:
    # Headless PKCE against staging on first use; the token stays in memory.
    client = TmsGatewayClient.for_environment(
        "staging",
        username=os.environ.get("TMS_USERNAME") or input("username: "),
        password=os.environ.get("TMS_PASSWORD") or getpass.getpass("password: "),
    )

    with open("examples/shipment.json", "r", encoding="utf-8") as handle:
        shipment_request = json.load(handle)

    shipment = client.create_shipment(shipment_request)
    shipment_id = shipment["id"]
    print(f"Created {shipment_id} in status {shipment['shipmentStatus']}")

    client.add_reference_number(shipment_id, "SO_NUMBER", "SO-559812")

    quote = client.quote_shipment(shipment_id)
    print(pretty(quote["rates"]))

    cheapest = min(quote["rates"], key=lambda rate: rate["totalCharge"])
    booked = client.book_shipment(shipment_id, {"selectedRateId": cheapest["id"], "dispatch": False})
    print(f"Booked with {booked.get('carrierName')} | BOL {booked.get('billNumber')}")

    print(pretty(client.get_shipment_tracking(shipment_id)))


if __name__ == "__main__":
    main()
