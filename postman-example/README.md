# Postman Example Collection for TMS Gateway

This Postman collection contains ready-to-run examples for authenticating with and calling the TMS Gateway API. It covers the full shipment lifecycle — creating shipments, getting rate quotes, booking, tracking, and more.

## Import

1. Open Postman and click **Import**.
2. Select the file `TMS Gateway Examples.postman_collection.json` from this folder.
3. The collection and its variables will be imported automatically.

## Setup — Collection Variables

Before running any requests, open the collection's **Variables** tab and fill in the values marked with placeholder text:

| Variable | What to enter |
|---|---|
| `loginEmail` | Your TMS login email address. |
| `loginPassword` | Your TMS login password. |
| `clientId` | Your OAuth client identifier (provided by eShipping). |
| `redirectUri` | The OAuth redirect URI configured for your client application. This must match the redirect URI registered for your TMS/eShipping OAuth client. |
| `AccountNumber` | Your TMS account number. |
| `OrganizationId` | Your organization GUID (provided by eShipping). |
| `subdomainSuffix` | Environment suffix. Use `-staging` for staging or leave blank for production. |

The remaining variables (`currentToken`, `state`, `codeVerifier`, `codeChallenge`, `code`, `currentShipmentId`, `currentRateId`, `currentDocumentLink`, etc.) are **auto-populated** by the collection's scripts as you run requests. You do not need to set them manually.

## Authentication

All API requests in the collection use a **Bearer Token** that is obtained through an OAuth 2.0 authorization-code flow with PKCE. You must run the three authentication requests **in order** before making any other calls:

1. **Login** — `POST /api/account/login`
   Authenticates your user session with email and password. The server sets session cookies that are required for the next step.

2. **Authorize** — `POST /connect/authorize`
   Initiates the PKCE flow. A pre-request script automatically generates the `state`, `codeVerifier`, and `codeChallenge`. The response redirects with an authorization `code` that is extracted by the test script.

3. **Get Token** — `POST /connect/token`
   Exchanges the authorization code and code verifier for an access token. The test script stores the token in `currentToken`, which is automatically attached as a Bearer token header on all subsequent requests.

> **Note:** Tokens expire after a period of time. When you receive a `401 Unauthorized` response, re-run the three authentication requests to obtain a fresh token.

## Collection Folders

### Shipment > Starting with an Incomplete Shipment

Demonstrates the workflow where you send eShipping a partial shipment and then rate-shop and finalize it through the API:

| # | Request | Description |
|---|---|---|
| 1 | **POST Shipment — Incomplete/Proposed** | Creates a shipment in `BUILDING` status with `isComplete: false`. The returned `shipmentId` is saved for subsequent calls. |
| 2 | **POST Quote a Shipment** | Requests rate quotes for the shipment. Returns a list of carrier rates with pricing, service days, and estimated delivery dates. The first rate's `id` is saved as `currentRateId`. |
| 3 | **POST Shipment Booking Options** | Books the shipment using the selected rate. Set `dispatch: true` to dispatch immediately. The shipment transitions to `BOOKED` status. |

If you only need to send incomplete shipments to eShipping and handle rate-shopping and booking through the TMS UI, only the first request is required.

### Shipment > Booking a Complete Shipment

Demonstrates sending a fully complete shipment that gets booked immediately:

| # | Request | Description |
|---|---|---|
| 1 | **POST Shipment — Complete providing carrier** | Creates a shipment in `BOOKED` status with `isComplete: true`, `dispatch: true`, and a specific `carrierScac`. The shipment is booked with the specified carrier. |
| 2 | **POST Shipment — Complete using lowest cost carrier** | Same as above, but instead of specifying a carrier, sets `bookLowestCostCarrier: true` to have eShipping automatically select the cheapest option. |
| 3 | **View BOL** | Opens the Bill of Lading document link returned from the booked shipment. |

### Shipment > Multi-Stop Shipment

Demonstrates sending a multi-stop shipment

| # | Request | Description |
|---|---|---|
| 1 | **POST Multi-Stop Shipment - BUILDING Complete Data** | Creates a shipment in `BUILDING` with multiple stops and all data filled in.  |
| 2 | **POST Multi-Stop Shipment - BUILDING no units to be finished in the UI** | Creates a shipment in `BUILDING` with multiple stops but no unit data. This is to demonstrate a shipment that will be finished vis the UI.  |
| 3 | **POST Multi-Stop Shipment - Complete/REQUESTED** | Creates a shipment in `REQUESTED` with multiple stops and all data filled in. When the Requested status is sent, the shipment is send to eShipping's team for booking. |

Notes on Multi-stop:
* FTL mode only
* Building or Requested status only
* does not use origin and destination, uses a stops array
* Quoting and booking are not supported via API
* Requested status indicates that the eShipping team should book the shipment


### Shipment > Shipment Utilities

Demonstrates common CRUD operations on shipments:

| Request | Description |
|---|---|
| **POST a shipment** | Creates a working shipment for use in the other utility requests. |
| **PUT Update a shipment** | Updates an existing shipment (full replacement of the shipment resource). |
| **GET Shipment** | Retrieves a shipment by its `shipmentId`. |
| **DELETE Shipment** | Deletes a shipment by its `shipmentId`. |
| **POST minimal shipment** | Creates a shipment with only the minimum required fields. |

### Shipment > Shipment Utilities > Shipment Search

Demonstrates searching for shipments

### Shipment > Shipment Utilities > Reference Numbers

| Request | Description |
|---|---|
| **POST Add a Reference Number to a shipment** | Adds a reference number to a shipment. |
| **DELETE Delete a Reference Number From a shipment** | Deletes a reference number from a shipment. |


### Quick Quote

Allows you to get rate quotes without creating a shipment:

| Request | Description |
|---|---|
| **POST Quote (V1)** | Rates based on weight and zip codes. |
| **POST Quote (V2)** | Rates based on weight, zip codes, and dimensions for more accurate pricing. **Recommended.** |

### Tracking

Look up shipment tracking information using different identifiers:

| Request | Description |
|---|---|
| **GET Track by ShipmentId** | Query parameter: `shipmentId` |
| **GET Track by Pro Number** | Query parameter: `proNumber` |
| **GET Track by Bill Number** | Query parameter: `billNumber` |
| **GET Track by eShipping Shipment ID** | Returns the tracking details for a shipment using the eShipping ShipmentID |

### Organizational Information

Endpoints used to retrieve organizational details

| Request | Description |
|---|---|
| **GET Carriers** | Returns the list of available carriers for your account. |
| **GET Organizations** | Returns the list of available organizations for your account. |


### Documents

Endpoints used for retrieving documents

| Request | Description |
|---|---|
| **GET documents for a shipment** | Returns the list of documents for a shipment. (NOTE: currently BOL and Pallet Label do not return from this call, but can be retrieved by calling GET Shipment |
| **GET a Shipments Document** | Example of using the link provided for a document to retrieve the document. |


## Environments

The collection uses the `subdomainSuffix` variable to target different environments:

| Environment | `subdomainSuffix` value | Gateway base URL |
|---|---|---|
| **Staging** | `-staging` (default) | `https://tmsgateway-staging.engagedtechnologies.com` |
| **Production** | *(empty string)* | `https://tmsgateway.engagedtechnologies.com` |

The identity provider URL follows the same pattern: `https://login.tms{subdomainSuffix}.engagedtechnologies.com`.

## Running the Collection

1. Set your collection variables as described in [Setup](#setup--collection-variables).
2. Run the three **Authentication** requests in order to obtain a token.
3. Run any of the shipment, quote, tracking, or carrier requests.

You can also use the Postman **Collection Runner** to execute folders in sequence. The authentication folder should be run first, followed by the shipment workflow of your choice.

