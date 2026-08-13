"""Tracking flows: by PRO number, bill number or shipment id."""

from typing import Any, Dict, List

from tms_gateway import TmsGatewayClient

from . import prompts

JsonDict = Dict[str, Any]


def track_flow(client: TmsGatewayClient) -> None:
    prompts.header("Track shipments")
    source = prompts.menu(
        "How do you want to track?",
        [
            "By PRO number(s)",
            "By bill number(s)",
            "By shipment id(s)",
            "Detail for one shipment id",
            "Provide a JSON body",
        ],
        back_label="Cancel",
    )
    if source is None:
        return

    if source == "Detail for one shipment id":
        shipment_id = prompts.ask("Shipment id", required=True)
        show_shipment_tracking(client, shipment_id)
        return

    if source == "Provide a JSON body":
        body = prompts.ask_json("tracking query body")
        if body is None:
            return
        results = prompts.run_guarded(
            lambda: client.track(
                pro_numbers=_as_list(body.get("proNumbers") or body.get("proNumber")),
                bill_numbers=_as_list(body.get("billNumbers") or body.get("billNumber")),
                shipment_ids=_as_list(body.get("shipmentIds") or body.get("shipmentId")),
            )
        )
    else:
        values = _ask_values(source)
        if not values:
            return
        kwargs = {
            "By PRO number(s)": {"pro_numbers": values},
            "By bill number(s)": {"bill_numbers": values},
            "By shipment id(s)": {"shipment_ids": values},
        }[source]
        results = prompts.run_guarded(lambda: client.track(**kwargs))

    if not results:
        prompts.warn("No tracking results were returned.")
        return

    display_tracking_results(results)

    if prompts.ask_yes_no("Show the full tracking detail for one of these?", default=False):
        index = prompts.ask_int(f"Which one (1-{len(results)})", required=True)
        if index and 1 <= index <= len(results):
            shipment_id = results[index - 1].get("shipmentId") or results[index - 1].get("id")
            if shipment_id:
                show_shipment_tracking(client, str(shipment_id))
            else:
                prompts.warn("That result does not carry a shipment id.")


def display_tracking_results(results: List[JsonDict]) -> None:
    prompts.table(
        "Tracking",
        ["#", "Shipment id", "Bill number", "PRO", "Carrier", "Status", "Status date", "Location"],
        [
            [
                index,
                item.get("shipmentId") or item.get("id"),
                item.get("billNumber") or item.get("name"),
                item.get("proNumber") or item.get("trackingNumber"),
                item.get("carrierName") or item.get("carrierScac"),
                _status(item),
                _status_date(item),
                _status_location(item),
            ]
            for index, item in enumerate(results, start=1)
        ],
    )


def show_shipment_tracking(client: TmsGatewayClient, shipment_id: str) -> None:
    tracking = prompts.run_guarded(lambda: client.get_shipment_tracking(shipment_id))
    if tracking is None:
        return

    prompts.header(
        f"Tracking for {tracking.get('billNumber') or shipment_id}",
        f"carrier {tracking.get('carrierName') or ''} | PRO {tracking.get('proNumber') or ''}",
    )

    stops = tracking.get("stops") or []
    if stops:
        prompts.table(
            "Stops",
            ["Seq", "City", "State", "Postal code", "Status"],
            [
                [
                    stop.get("sequenceNumber"),
                    stop.get("city"),
                    stop.get("stateCode"),
                    stop.get("postalCode"),
                    stop.get("stopStatus"),
                ]
                for stop in stops
            ],
        )

    events = tracking.get("trackingEvents") or tracking.get("events") or []
    if events:
        prompts.table(
            "Tracking events",
            ["Date", "Status", "Description", "Location"],
            [
                [
                    event.get("dateTime") or event.get("date"),
                    event.get("status") or event.get("trackingStatus"),
                    event.get("description") or event.get("statusDescription"),
                    _status_location(event),
                ]
                for event in events
            ],
        )

    if not stops and not events:
        prompts.show_json(tracking, title=f"Tracking {shipment_id}")


def _ask_values(source: str) -> List[str]:
    label = {
        "By PRO number(s)": "PRO number(s)",
        "By bill number(s)": "Bill number(s)",
        "By shipment id(s)": "Shipment id(s)",
    }[source]
    raw = prompts.ask(f"{label} (comma separated)", required=True) or ""
    return [value.strip() for value in raw.split(",") if value.strip()]


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def _status(item: JsonDict) -> str:
    event = item.get("trackingEvent") or item.get("latestTrackingEvent") or {}
    return str(item.get("trackingStatus") or event.get("status") or item.get("shipmentStatus") or "")


def _status_date(item: JsonDict) -> str:
    event = item.get("trackingEvent") or item.get("latestTrackingEvent") or {}
    return str(item.get("dateTime") or event.get("dateTime") or "")


def _status_location(item: JsonDict) -> str:
    event = item.get("trackingEvent") or item.get("latestTrackingEvent") or item
    parts = [event.get("city"), event.get("stateCode") or event.get("state"), event.get("postalCode")]
    return ", ".join(str(part) for part in parts if part)
