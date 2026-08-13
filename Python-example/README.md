# TMS Gateway Python client + console

A shareable Python class (`tms_gateway.TmsGatewayClient`) for the Engaged Technologies TMS
Gateway API, plus an interactive terminal program (`tms_cli`) built on top of it.

## Install

### Windows (PowerShell)

Easiest: from the folder that contains this README, run the launcher - it creates the virtual
environment, installs the dependencies and starts the console.

```powershell
cd C:\path\to\tms-gateway-python
.\run.ps1 --environment qa --username me@engagedtechnologies.com
```

If PowerShell blocks the script, allow it for this window only with
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, or use `run.cmd` instead.

The same thing by hand (note: PowerShell has no `&&` and no `source`, so run one line at a
time, and activation uses `Activate.ps1`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m tms_cli --environment qa
```

Without activating, call the interpreter inside the virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m tms_cli --environment qa
```

`ModuleNotFoundError: No module named 'requests'` means the install step has not run in the
interpreter you are using; `No module named tms_cli` means the current directory is not the
folder that contains `tms_cli\`.

### macOS / Linux

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # or: pip install -e .
```

## Run the console

```bash
python -m tms_cli                              # staging (default), prompts for username/password
python -m tms_cli --environment qa --username me@example.com
python -m tms_cli --browser-login              # sign in through a browser instead
python -m tms_cli --browser-login --no-browser # browser flow, prints the authorize url
```

The console signs in first, then offers **Create shipment**, **Quick quote**, **Track**,
**Open a shipment by id** and **Find shipments**.

### Authentication

OAuth2 authorization code + PKCE against the TMS identity server, using the `Sandbox` client.

The default is the **headless flow the Postman collection uses** - no browser and no
localhost listener (`HeadlessPkceAuthenticator`):

1. `POST /api/account/login` with the username and password for the identity cookie.
2. `POST /connect/authorize` (`response_type=code`, `code_challenge_method=S256`) **without
   following redirects**; the authorization code is read from the `Location` response header.
3. `POST /connect/token` with that code and the PKCE verifier.

Credentials come from `--username` / a prompt and the `TMS_PASSWORD` environment variable or
a hidden prompt. They and the token are held **in memory only** - nothing is written to disk.
The `Sandbox` client has no refresh token, so when the token expires - or if the gateway ever
answers `401` - the same flow runs again automatically on the next call.

`--browser-login` uses the original browser flow instead (`PkceAuthenticator`): it opens the
identity server and listens on `http://localhost:5555/auth` for the redirect.

```python
from tms_gateway import HeadlessPkceAuthenticator, TmsGatewayClient, get_environment

client = TmsGatewayClient(
    HeadlessPkceAuthenticator(username, password, get_environment("qa")),
    get_environment("qa"),
)
```

Override the client, redirect uri or scopes if you have your own registration:

```bash
python -m tms_cli --client-id MyClient --redirect-uri http://localhost:5000/auth \
    --scope openid --scope gatewayShipments --scope gatewayRates --scope gatewayTrackings
```

### Environments

| Name | Gateway | Identity server |
| --- | --- | --- |
| `staging` (default) | `https://tmsgateway-staging.engagedtechnologies.com` | `https://login.tms-staging.engagedtechnologies.com` |
| `qa` | `https://tmsgateway-qa.engagedtechnologies.com` | `https://login.tms-qa.engagedtechnologies.com` |
| `production` | `https://tmsgateway.engagedtechnologies.com` | `https://login.tms.engagedtechnologies.com` |

## Flows

**Create shipment** - either answer the prompts (LTL or FTL, origin plus a second stop, then
"do you want an additional stop", one or more units, reference numbers, accessorials) or paste
/ point at a JSON body. Two gateway rules the prompts follow: a `BUILDING` shipment needs at
least one reference number, and origin/destination accessorials belong on the stop they apply
to - the gateway rejects them in the shipment level `accessorials` collection whenever `stops`
is used. After the shipment exists, a `BUILDING` shipment can be **updated** or
**quoted**; the quote prints the rate table and you can select a rate and book it. Choosing
anything other than the cheapest rate prompts for a reason type, which is what the gateway
requires. Reference numbers can be added or deleted at any time from the shipment menu.

**Quick quote** - paste a JSON body, or answer the prompts. If you have dimensions the request
goes to version 2 of `POST /quotes` (a `units` collection that accepts length/width/height); if
you do not, it goes to version 1 (a single `totalWeight` + `freightClass`). Freight class is
only asked for LTL equipment.

**Track** - by PRO number(s), bill number(s), shipment id(s), a JSON body, or full detail
(stops and tracking events) for a single shipment id.

Sample bodies live in `examples/`.

## Using the class on its own

```python
from tms_gateway import TmsGatewayClient

client = TmsGatewayClient.for_environment("staging", username, password)  # sign-in on first call

shipment = client.create_shipment({...})
client.add_reference_number(shipment["id"], "PO_NUMBER", "PO-100234")

quote = client.quote_shipment(shipment["id"])
cheapest = min(quote["rates"], key=lambda rate: rate["totalCharge"])
client.book_shipment(shipment["id"], {"selectedRateId": cheapest["id"], "dispatch": True})

client.track(pro_numbers=["123456789"])
```

Already have a token (a service, a test, a shared session)?

```python
from tms_gateway import TmsGatewayClient, StaticTokenAuthenticator, get_environment

client = TmsGatewayClient(StaticTokenAuthenticator(access_token), get_environment("qa"))
```

### Methods

| Method | Endpoint |
| --- | --- |
| `create_shipment(body)` | `POST /shipments` |
| `get_shipment(id)` | `GET /shipments/{id}` |
| `update_shipment(body)` | `PUT /shipments` |
| `cancel_shipment(id)` | `DELETE /shipments/{id}` |
| `list_shipments(...)` | `GET /shipments` |
| `search_shipments(...)` | `GET /shipments/search` |
| `get_shipment_documents(id)` | `GET /shipments/{id}/documents` |
| `add_reference_number(id, type, value)` | `POST /shipments/{id}/referenceNumbers` |
| `delete_reference_number(id, referenceNumberId)` | `DELETE /shipments/{id}/referenceNumbers/{referenceNumberId}` |
| `quote_shipment(id)` | `POST /shipments/{id}/quotes` |
| `quick_quote(body, api_version)` | `POST /quotes` (v1 or v2) |
| `book_shipment(id, bookingOptions)` | `POST /shipments/{id}/bookingOptions` |
| `track(pro_numbers, bill_numbers, shipment_ids)` | `GET /trackings` |
| `get_shipment_tracking(id)` | `GET /shipments/{id}/trackings` |
| `get_carriers()`, `get_organizations()` | `GET /carriers`, `GET /organizations` |

Failures raise `ApiError` (with `NotFoundError` and `ValidationError` subclasses) carrying the
status code, the problem details body and the `tms-error-type` / `tms-error-location-code`
headers the gateway returns.

Valid enum values (modes, equipment types, freight classes, package types, accessorials,
reference number types, ...) are in `tms_gateway.enums`.

## Tests

```bash
python -m pytest
```

The tests stub the HTTP layer, so nothing is sent to a real environment.

## Verified against QA

Sign in, `POST /shipments` (BUILDING), `GET /shipments/{id}`, `GET /shipments?...`,
reference number add/list/delete, `POST /shipments/{id}/quotes`, `GET /trackings`,
`DELETE /shipments/{id}` and quick quote v1/v2 were all exercised live against QA. Two
observations about QA data (not the client): quick quote **v1** answers `200` with an empty
`rates` list for every lane tried, while **v2** returns full rate tables, and
`POST /shipments/{id}/quotes` returned no rates for the QA account that was available, so
selecting a rate and booking has only been exercised against the offline fake.
