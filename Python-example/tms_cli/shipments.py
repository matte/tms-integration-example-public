"""Create, update, quote, book and maintain shipments from the console."""

from typing import Any, Dict, List, Optional

from tms_gateway import TmsGatewayClient
from tms_gateway import enums

from . import prompts
from .quotes import display_quote, select_rate_and_book
from .tracking import show_shipment_tracking

JsonDict = Dict[str, Any]


def create_shipment_flow(client: TmsGatewayClient) -> None:
    prompts.header("Create shipment")
    source = prompts.menu(
        "How do you want to build the shipment?",
        ["Enter values step by step", "Provide a JSON body"],
        back_label="Cancel",
    )
    if source is None:
        return

    if source == "Provide a JSON body":
        body = prompts.ask_json("shipment body")
        if body is None:
            return
    else:
        body = build_shipment_body()
        prompts.show_json(body, title="Shipment request")
        if not prompts.ask_yes_no("Send this to the gateway?", default=True):
            return

    shipment = prompts.run_guarded(lambda: client.create_shipment(body))
    if shipment is None:
        return

    prompts.success(
        f"Created shipment {_shipment_id(shipment)} "
        f"(name {shipment.get('name')}, status {shipment.get('shipmentStatus')})"
    )
    shipment_menu(client, shipment)


# ----------------------------------------------------------------------
# Guided shipment construction
# ----------------------------------------------------------------------
def _shipment_id(shipment: JsonDict) -> Optional[str]:
    """The gateway returns ``id``; some collections still use ``shipmentId``."""
    return shipment.get("id") or shipment.get("shipmentId")


def build_shipment_body() -> JsonDict:
    account_number = prompts.ask("Account number", required=True)
    mode = prompts.ask_choice("Mode", ["LTL", "FTL"], default="LTL")
    equipment_options = enums.LTL_EQUIPMENT_TYPES if mode == "LTL" else enums.FTL_EQUIPMENT_TYPES
    equipment_type = prompts.ask_choice(
        "Equipment type", equipment_options, default=equipment_options[0]
    )
    service_level = prompts.ask_choice("Service level", enums.SERVICE_LEVELS, default="STANDARD")
    shipment_status = prompts.ask_choice(
        "Shipment status", enums.WRITABLE_SHIPMENT_STATUSES, default="BUILDING"
    )

    requested_pickup = prompts.ask("Requested pickup date (YYYY-MM-DD)")
    requested_delivery = prompts.ask("Requested delivery date (YYYY-MM-DD)")

    stops: List[JsonDict] = [build_stop(1, "Origin", "ORIGIN")]
    stops.append(build_stop(2, "Destination", "DESTINATION"))
    sequence = 3
    while prompts.ask_yes_no("Do you want to add an additional stop?", default=False):
        stops.append(build_stop(sequence, f"Stop {sequence}", "DESTINATION"))
        sequence += 1

    units: List[JsonDict] = [build_unit(1, require_freight_class=mode == "LTL")]
    unit_number = 2
    while prompts.ask_yes_no("Do you want to add another unit?", default=False):
        units.append(build_unit(unit_number, require_freight_class=mode == "LTL"))
        unit_number += 1

    reference_numbers = build_reference_numbers(require_one=shipment_status == "BUILDING")
    accessorials = build_accessorials()

    shipment: JsonDict = {
        "accountNumber": account_number,
        "mode": mode,
        "equipmentType": equipment_type,
        "serviceLevel": service_level,
        "shipmentStatus": shipment_status,
        "isComplete": prompts.ask_yes_no("Is the shipment data complete?", default=True),
        "stops": stops,
        "units": units,
    }
    if requested_pickup:
        shipment["requestedPickupDate"] = requested_pickup
    if requested_delivery:
        shipment["requestedDeliveryDate"] = requested_delivery
    if reference_numbers:
        shipment["referenceNumbers"] = reference_numbers
    if accessorials:
        shipment["accessorials"] = accessorials

    carrier_scac = prompts.ask("Carrier SCAC (blank to let the TMS choose)")
    if carrier_scac:
        shipment["carrierScac"] = carrier_scac

    return shipment


def build_stop(sequence_number: int, label: str, accessorial_type: str = "ORIGIN") -> JsonDict:
    prompts.header(f"{label} (stop {sequence_number})")
    stop: JsonDict = {
        "sequenceNumber": sequence_number,
        "name": prompts.ask("Location name", required=True),
        "address1": prompts.ask("Address line 1", required=True),
        "city": prompts.ask("City", required=True),
        "stateCode": prompts.ask("State / province code", required=True),
        "postalCode": prompts.ask("Postal code", required=True),
        "countryCode": prompts.ask("Country code", default="US"),
    }

    address2 = prompts.ask("Address line 2")
    if address2:
        stop["address2"] = address2

    location_direction_type = prompts.ask_choice(
        "Location direction type", enums.LOCATION_DIRECTION_TYPES, allow_blank=True
    )
    if location_direction_type:
        stop["locationDirectionType"] = location_direction_type

    contact_name = prompts.ask("Contact name")
    if contact_name:
        stop["contactName"] = contact_name
    contact_phone = prompts.ask("Contact phone")
    if contact_phone:
        stop["contactPhone"] = contact_phone
    contact_email = prompts.ask("Contact email")
    if contact_email:
        stop["contactEmails"] = [contact_email]

    for label_text, key in (("Earliest scheduled date (YYYY-MM-DD)", "earliestScheduledDate"),
                            ("Latest scheduled date (YYYY-MM-DD)", "latestScheduledDate"),
                            ("Open time (HH:MM)", "openTime"),
                            ("Close time (HH:MM)", "closeTime")):
        value = prompts.ask(label_text)
        if value:
            stop[key] = value

    special_instructions = prompts.ask("Special instructions")
    if special_instructions:
        stop["specialInstructions"] = special_instructions

    # Origin/destination accessorials belong on the stop; the gateway rejects
    # them in the shipment level accessorials collection when stops are used.
    codes = prompts.ask_multi_choice(
        f"{label} accessorials", enums.ACCESSORIALS_BY_TYPE[accessorial_type]
    )
    if codes:
        stop["accessorials"] = [
            {"accessorialCode": code, "accessorialType": accessorial_type} for code in codes
        ]

    return stop


def build_unit(index: int, require_freight_class: bool) -> JsonDict:
    prompts.header(f"Unit {index}")
    unit: JsonDict = {
        "description": prompts.ask("Description", required=True),
        "quantity": prompts.ask_int("Quantity", default=1),
        "packageType": prompts.ask_choice("Package type", enums.PACKAGE_TYPES, default="PALLETS"),
        "weight": prompts.ask_decimal("Weight (lb, total for the quantity)"),
        "weightUnitOfMeasure": "LB",
    }

    if require_freight_class:
        unit["freightClass"] = prompts.ask_choice(
            "Freight class", enums.FREIGHT_CLASSES, default="FREIGHT_CLASS_100"
        )

    if prompts.ask_yes_no("Do you have dimensions for this unit?", default=False):
        unit["length"] = prompts.ask_decimal("Length (in)")
        unit["width"] = prompts.ask_decimal("Width (in)")
        unit["height"] = prompts.ask_decimal("Height (in)")
        unit["dimensionsUnitOfMeasure"] = "IN"

    nmfc = prompts.ask("NMFC")
    if nmfc:
        unit["nmfc"] = nmfc

    unit["isStackable"] = prompts.ask_yes_no("Is this unit stackable?", default=False)
    return unit


def build_reference_numbers(require_one: bool = False) -> List[JsonDict]:
    """A BUILDING shipment is rejected by the gateway without a reference number."""
    references: List[JsonDict] = []
    if require_one:
        prompts.header(
            "Reference number", "A shipment in BUILDING status needs at least one"
        )
        references.append(
            {
                "type": prompts.ask_choice(
                    "Reference number type", enums.REFERENCE_NUMBER_TYPES, default="PO_NUMBER"
                ),
                "value": prompts.ask("Reference number value", required=True),
            }
        )
    while prompts.ask_yes_no("Add a reference number?", default=False):
        reference_type = prompts.ask_choice(
            "Reference number type", enums.REFERENCE_NUMBER_TYPES, default="PO_NUMBER"
        )
        value = prompts.ask("Reference number value", required=True)
        references.append({"type": reference_type, "value": value})
    return references


def build_accessorials() -> List[JsonDict]:
    """Shipment level accessorials; origin/destination ones are asked per stop."""
    accessorials: List[JsonDict] = []
    if not prompts.ask_yes_no("Add product or shipment accessorials?", default=False):
        return accessorials
    for accessorial_type in ("PRODUCT", "SHIPMENT"):
        codes = prompts.ask_multi_choice(
            f"{accessorial_type} accessorials", enums.ACCESSORIALS_BY_TYPE[accessorial_type]
        )
        for code in codes:
            accessorials.append({"accessorialCode": code, "accessorialType": accessorial_type})
    return accessorials


# ----------------------------------------------------------------------
# Working with an existing shipment
# ----------------------------------------------------------------------
def open_shipment_flow(client: TmsGatewayClient) -> None:
    prompts.header("Open an existing shipment")
    shipment_id = prompts.ask("Shipment id", required=True)
    shipment = prompts.run_guarded(lambda: client.get_shipment(shipment_id))
    if shipment:
        shipment_menu(client, shipment)


def shipment_menu(client: TmsGatewayClient, shipment: JsonDict) -> None:
    shipment_id = _shipment_id(shipment)
    while True:
        status = str(shipment.get("shipmentStatus", "")).upper()
        prompts.header(
            f"Shipment {shipment.get('name') or shipment_id}",
            f"id {shipment_id} | status {status or 'UNKNOWN'}",
        )

        options = ["View shipment JSON", "Reference numbers", "Tracking"]
        if status == "BUILDING":
            # A building shipment can still be changed, and it is the only state
            # from which quoting and booking makes sense.
            options = ["Update shipment", "Quote shipment"] + options
        if status not in ("CANCELED",):
            options.append("Cancel shipment")
        options.append("Refresh")

        choice = prompts.menu("What next?", options, back_label="Back to main menu")
        if choice is None:
            return

        if choice == "Update shipment":
            updated = update_shipment_flow(client, shipment)
            if updated:
                shipment = updated
        elif choice == "Quote shipment":
            quote_and_book_flow(client, shipment_id)
            shipment = prompts.run_guarded(lambda: client.get_shipment(shipment_id)) or shipment
        elif choice == "Reference numbers":
            reference_number_menu(client, shipment_id)
            shipment = prompts.run_guarded(lambda: client.get_shipment(shipment_id)) or shipment
        elif choice == "Tracking":
            show_shipment_tracking(client, shipment_id)
        elif choice == "View shipment JSON":
            prompts.show_json(shipment, title=f"Shipment {shipment_id}")
        elif choice == "Cancel shipment":
            if prompts.ask_yes_no("Cancel this shipment in the TMS?", default=False):
                prompts.run_guarded(lambda: client.cancel_shipment(shipment_id))
                prompts.success("Cancel request sent.")
                shipment = prompts.run_guarded(lambda: client.get_shipment(shipment_id)) or shipment
        elif choice == "Refresh":
            shipment = prompts.run_guarded(lambda: client.get_shipment(shipment_id)) or shipment


def update_shipment_flow(client: TmsGatewayClient, shipment: JsonDict) -> Optional[JsonDict]:
    """PUT /shipments with the fields the gateway allows to be updated."""
    shipment_id = _shipment_id(shipment)
    prompts.header("Update shipment", "Blank answers keep the current value")

    if prompts.ask_yes_no("Provide the update as a JSON body instead?", default=False):
        body = prompts.ask_json("shipment update body")
        if body is None:
            return None
        body.setdefault("id", shipment_id)
    else:
        current_mode = str(shipment.get("mode") or "LTL")
        mode = prompts.ask_choice("Mode", ["LTL", "FTL"], default=current_mode if current_mode in ("LTL", "FTL") else "LTL")
        equipment_options = enums.LTL_EQUIPMENT_TYPES if mode == "LTL" else enums.FTL_EQUIPMENT_TYPES
        current_equipment = str(shipment.get("equipmentType") or equipment_options[0])
        body = {
            "id": shipment_id,
            "mode": mode,
            "equipmentType": prompts.ask_choice(
                "Equipment type",
                equipment_options,
                default=current_equipment if current_equipment in equipment_options else equipment_options[0],
            ),
            "serviceLevel": prompts.ask_choice(
                "Service level", enums.SERVICE_LEVELS, default=str(shipment.get("serviceLevel") or "STANDARD")
            ),
            "shipmentStatus": prompts.ask_choice(
                "Shipment status", enums.WRITABLE_SHIPMENT_STATUSES, default="BUILDING"
            ),
            "requestedPickupDate": prompts.ask(
                "Requested pickup date (YYYY-MM-DD)", default=shipment.get("requestedPickupDate") or ""
            ),
            "requestedDeliveryDate": prompts.ask(
                "Requested delivery date (YYYY-MM-DD)", default=shipment.get("requestedDeliveryDate") or ""
            ),
            "units": list(shipment.get("units") or []),
        }
        body = {key: value for key, value in body.items() if value not in (None, "")}

        if prompts.ask_yes_no("Replace the units on this shipment?", default=False):
            units = [build_unit(1, require_freight_class=body.get("mode") == "LTL")]
            index = 2
            while prompts.ask_yes_no("Do you want to add another unit?", default=False):
                units.append(build_unit(index, require_freight_class=body.get("mode") == "LTL"))
                index += 1
            body["units"] = units

    prompts.show_json(body, title="Shipment update")
    if not prompts.ask_yes_no("Send this update?", default=True):
        return None

    updated = prompts.run_guarded(lambda: client.update_shipment(body))
    if updated is None:
        return None
    prompts.success("Shipment updated.")
    return updated if _shipment_id(updated) else client.get_shipment(shipment_id)


def quote_and_book_flow(client: TmsGatewayClient, shipment_id: str) -> None:
    prompts.header("Quote shipment", f"shipment {shipment_id}")
    quote = prompts.run_guarded(lambda: client.quote_shipment(shipment_id))
    if quote is None:
        return

    display_quote(quote)
    select_rate_and_book(client, shipment_id, quote)


def reference_number_menu(client: TmsGatewayClient, shipment_id: str) -> None:
    while True:
        references = prompts.run_guarded(lambda: client.get_reference_numbers(shipment_id))
        if references is None:
            return

        prompts.table(
            f"Reference numbers on {shipment_id}",
            ["#", "Type", "Value", "Primary", "Id"],
            [
                [
                    index,
                    reference.get("type"),
                    reference.get("value"),
                    reference.get("isPrimary"),
                    reference.get("id"),
                ]
                for index, reference in enumerate(references, start=1)
            ],
        )

        choice = prompts.menu("Reference numbers", ["Add", "Delete"], back_label="Back")
        if choice is None:
            return

        if choice == "Add":
            reference_type = prompts.ask_choice(
                "Reference number type", enums.REFERENCE_NUMBER_TYPES, default="PO_NUMBER"
            )
            value = prompts.ask("Value", required=True)
            if prompts.run_guarded(
                lambda: client.add_reference_number(shipment_id, reference_type, value)
            ) is not None:
                prompts.success("Reference number added.")
        elif choice == "Delete":
            if not references:
                prompts.warn("There are no reference numbers to delete.")
                continue
            labels = [
                f"{reference.get('type')} = {reference.get('value')} ({reference.get('id')})"
                for reference in references
            ]
            selected = prompts.ask_choice("Which reference number?", labels, allow_blank=True)
            if not selected:
                continue
            reference = references[labels.index(selected)]
            reference_id = reference.get("id")
            if not reference_id:
                prompts.error("That reference number has no id and cannot be deleted.")
                continue
            if prompts.ask_yes_no(f"Delete {selected}?", default=False):
                if prompts.run_guarded(
                    lambda: client.delete_reference_number(shipment_id, reference_id)
                ) is not None:
                    prompts.success("Reference number deleted.")


def find_shipments_flow(client: TmsGatewayClient) -> None:
    prompts.header("Find shipments")
    query = prompts.ask("Search text (bill number, PO, name, ...)", required=True)
    status = prompts.ask_choice("Filter by status", enums.SHIPMENT_STATUSES, allow_blank=True)

    result = prompts.run_guarded(lambda: client.search_shipments(query=query, shipment_status=status))
    if result is None:
        return

    items = result.get("items") or result.get("shipments") or []
    if not items:
        prompts.warn("No shipments matched.")
        return

    prompts.table(
        "Shipments",
        ["#", "Shipment id", "Name", "Status", "Origin", "Destination"],
        [
            [
                index,
                _shipment_id(item),
                item.get("name") or item.get("billNumber"),
                item.get("shipmentStatus"),
                _location(item.get("origin")),
                _location(item.get("destination")),
            ]
            for index, item in enumerate(items, start=1)
        ],
    )

    if prompts.ask_yes_no("Open one of these shipments?", default=True):
        index = prompts.ask_int(f"Which one (1-{len(items)})", required=True)
        if index and 1 <= index <= len(items):
            shipment_id = _shipment_id(items[index - 1])
            shipment = prompts.run_guarded(lambda: client.get_shipment(shipment_id))
            if shipment:
                shipment_menu(client, shipment)


def _location(stop: Optional[JsonDict]) -> str:
    if not stop:
        return ""
    parts = [stop.get("city"), stop.get("stateCode"), stop.get("postalCode")]
    return ", ".join(str(part) for part in parts if part)
