"""Quick quotes, rate display and booking."""

from typing import Any, Dict, List, Optional

from tms_gateway import TmsGatewayClient
from tms_gateway import enums

from . import prompts

JsonDict = Dict[str, Any]


def quick_quote_flow(client: TmsGatewayClient) -> None:
    prompts.header("Quick quote", "Rate a lane without creating a shipment")
    source = prompts.menu(
        "How do you want to build the quote?",
        ["Enter values step by step", "Provide a JSON body"],
        back_label="Cancel",
    )
    if source is None:
        return

    if source == "Provide a JSON body":
        body = prompts.ask_json("quick quote body")
        if body is None:
            return
        # v2 of the endpoint carries a units collection (dimensions supported),
        # v1 only takes a single total weight and freight class.
        version = "2" if "units" in body else "1"
    else:
        body, version = build_quick_quote_body()
        prompts.show_json(body, title=f"Quick quote request (api version {version})")
        if not prompts.ask_yes_no("Send this to the gateway?", default=True):
            return

    quote = prompts.run_guarded(lambda: client.quick_quote(body, api_version=version))
    if quote is None:
        return
    display_quote(quote)


def build_quick_quote_body() -> tuple:
    """Collect quick quote parameters; returns the body and the api version to use."""
    origin_postal_code = prompts.ask("Origin postal code", required=True)
    origin_country_code = prompts.ask("Origin country code", default="US")
    destination_postal_code = prompts.ask("Destination postal code", required=True)
    destination_country_code = prompts.ask("Destination country code", default="US")

    organization_id = prompts.ask("Organization id (blank to use the token's organization)")

    has_dimensions = prompts.ask_yes_no(
        "Do you have dimensions for the freight?", default=False
    )

    origin_accessorials = prompts.ask_multi_choice("Origin accessorials", enums.ORIGIN_ACCESSORIALS)
    destination_accessorials = prompts.ask_multi_choice(
        "Destination accessorials", enums.DESTINATION_ACCESSORIALS
    )
    product_accessorials = prompts.ask_multi_choice("Product accessorials", enums.PRODUCT_ACCESSORIALS)
    shipment_accessorials = prompts.ask_multi_choice("Shipment accessorials", enums.SHIPMENT_ACCESSORIALS)

    body: JsonDict = {
        "originPostalCode": origin_postal_code,
        "destinationPostalCode": destination_postal_code,
    }
    if organization_id:
        body["organizationId"] = organization_id
    for key, values in (
        ("originAccessorials", origin_accessorials),
        ("destinationAccessorials", destination_accessorials),
        ("productAccessorials", product_accessorials),
        ("shipmentAccessorials", shipment_accessorials),
    ):
        if values:
            body[key] = values

    if not has_dimensions:
        # Version 1: a single total weight and freight class for the whole shipment.
        body["totalWeight"] = prompts.ask_decimal("Total weight (lb)")
        body["freightClass"] = prompts.ask_choice(
            "Freight class", enums.FREIGHT_CLASSES, default="FREIGHT_CLASS_100"
        )
        return body, "1"

    # Version 2: a units collection, which is where dimensions are accepted.
    body["originCountryCode"] = origin_country_code
    body["destinationCountryCode"] = destination_country_code

    origin_location_type = prompts.ask_choice(
        "Origin location type", enums.LOCATION_DIRECTION_TYPES, allow_blank=True
    )
    if origin_location_type:
        body["originLocationType"] = origin_location_type
    destination_location_type = prompts.ask_choice(
        "Destination location type", enums.LOCATION_DIRECTION_TYPES, allow_blank=True
    )
    if destination_location_type:
        body["destinationLocationType"] = destination_location_type

    equipment_type = prompts.ask_choice(
        "Equipment type", enums.EQUIPMENT_TYPES, default="LTL_DRY_VAN"
    )
    body["equipmentType"] = equipment_type

    units: List[JsonDict] = [build_quick_quote_unit(1, equipment_type)]
    index = 2
    while prompts.ask_yes_no("Do you want to add another unit?", default=False):
        units.append(build_quick_quote_unit(index, equipment_type))
        index += 1
    body["units"] = units

    return body, "2"


def build_quick_quote_unit(index: int, equipment_type: str) -> JsonDict:
    prompts.header(f"Quick quote unit {index}")
    unit: JsonDict = {
        "quantity": prompts.ask_int("Quantity", default=1),
        "packageType": prompts.ask_choice("Package type", enums.PACKAGE_TYPES, default="PALLETS"),
        "totalWeight": prompts.ask_decimal("Total weight for this unit line (lb)"),
        "length": prompts.ask_decimal("Length (in)"),
        "width": prompts.ask_decimal("Width (in)"),
        "height": prompts.ask_decimal("Height (in)"),
    }

    # Freight class is only required for LTL equipment.
    if equipment_type == "LTL_DRY_VAN":
        unit["freightClass"] = prompts.ask_choice(
            "Freight class", enums.FREIGHT_CLASSES, default="FREIGHT_CLASS_100"
        )

    description = prompts.ask("Description")
    if description:
        unit["description"] = description
    unit["isHazmat"] = prompts.ask_yes_no("Is this unit hazmat?", default=False)
    return unit


# ----------------------------------------------------------------------
# Rate display and booking
# ----------------------------------------------------------------------
def display_quote(quote: JsonDict) -> None:
    rates = rates_of(quote)
    if not rates:
        prompts.warn("The quote came back without any rates.")
        prompts.show_json(quote, title="Quote")
        return

    prompts.table(
        f"Rates for quote {quote.get('quoteNumber') or ''} (distance {quote.get('distance', 'n/a')})",
        ["#", "Carrier", "SCAC", "Mode", "Service level", "Transit days", "Est. delivery", "Total", "Guaranteed"],
        [
            [
                index,
                rate.get("carrierName"),
                rate.get("displayScac"),
                rate.get("mode"),
                rate.get("serviceLevel"),
                rate.get("serviceDays"),
                rate.get("estimatedDeliveryDate"),
                _money(rate.get("totalCharge"), rate.get("currencyType")),
                _money(rate.get("guaranteedTotalCharge"), rate.get("currencyType")),
            ]
            for index, rate in enumerate(rates, start=1)
        ],
    )

    alternate_options = quote.get("alternateOptions") or []
    if alternate_options:
        prompts.table(
            "Alternate booking options",
            ["Option", "Description"],
            [[option.get("optionType"), option.get("description")] for option in alternate_options],
        )


def select_rate_and_book(client: TmsGatewayClient, shipment_id: str, quote: JsonDict) -> None:
    rates = rates_of(quote)
    if not rates:
        return
    if not prompts.ask_yes_no("Select a rate and book this shipment?", default=True):
        return

    index = prompts.ask_int(f"Which rate (1-{len(rates)})", required=True)
    if not index or not (1 <= index <= len(rates)):
        prompts.error("That is not one of the listed rates.")
        return
    rate = rates[index - 1]

    booking_options: JsonDict = {
        "selectedRateId": rate.get("id"),
        "dispatch": prompts.ask_yes_no("Dispatch the shipment as part of booking?", default=False),
    }

    if rate.get("serviceLevel"):
        booking_options["serviceLevel"] = rate["serviceLevel"]
    if rate.get("carrierId"):
        booking_options["carrier"] = {"id": rate["carrierId"], "scac": rate.get("displayScac")}

    cheapest = min(rates, key=lambda item: _as_float(item.get("totalCharge")))
    if rate is not cheapest:
        prompts.warn(
            f"{rate.get('carrierName')} is not the cheapest rate "
            f"({_money(cheapest.get('totalCharge'))} from {cheapest.get('carrierName')}), "
            "so a reason is required."
        )
        booking_options["selectedReasonType"] = prompts.ask_choice(
            "Reason for not selecting the cheapest rate",
            enums.SELECTED_REASON_TYPES,
            default="CUSTOMER_SPECIFIED",
        )
        description = prompts.ask("Reason description")
        if description:
            booking_options["selectedReasonDescription"] = description

    prompts.show_json(booking_options, title="Booking options")
    if not prompts.ask_yes_no("Book it?", default=True):
        return

    booked = prompts.run_guarded(lambda: client.book_shipment(shipment_id, booking_options))
    if booked is None:
        return

    prompts.success(
        f"Booked. Status {booked.get('shipmentStatus')} | carrier {booked.get('carrierName')} "
        f"| BOL {booked.get('billNumber')} | PRO {booked.get('trackingNumber')}"
    )
    prompts.show_json(booked, title="Booked shipment")


def rates_of(quote: JsonDict) -> List[JsonDict]:
    return list(quote.get("rates") or [])


def _money(amount: Any, currency: Optional[str] = None) -> str:
    if amount in (None, ""):
        return ""
    return f"{float(amount):,.2f} {currency or ''}".strip()


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")
