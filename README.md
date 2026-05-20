# TMS Integration Example

A reference .NET 6 application that demonstrates how to integrate with the Engaged Technologies TMS Gateway API. It reads mock order and address data from local JSON files, transforms them into TMS Gateway shipment resources, authenticates via OpenID Connect (PKCE), and posts shipments to the gateway.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Solution Structure](#solution-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Running Tests](#running-tests)
- [Postman Collection](#postman-collection)

## Prerequisites

- [.NET 6.0 SDK](https://dotnet.microsoft.com/download/dotnet/6.0) or later
- A TMS Gateway account (account number, email, and password)
- Visual Studio 2022+ or the `dotnet` CLI

## Solution Structure

```
TmsIntegrationExample.sln
├── src/
│   ├── TmsIntegrationExample.Example        # Hosted background job that runs the integration
│   │   ├── Program.cs                       # Application entry point
│   │   ├── Startup.cs                       # DI and service configuration
│   │   ├── TmsIntegrationExampleJob.cs      # BackgroundService that triggers processing
│   │   ├── TmsIntegrationExampleProcessor.cs# Reads mock data, transforms, and posts shipments
│   │   ├── Transformers/
│   │   │   ├── MockOrderToShipment.cs       # Order → ShipmentPost transformer
│   │   │   └── MockAddressToGatewayStop.cs  # Address → Stop transformer
│   │   └── Extensions/
│   │       ├── FormatExtensions.cs          # Phone and country code formatting helpers
│   │       └── PathExtensions.cs            # Assembly-relative path resolution
│   │
│   └── TmsIntegrationExample.Services       # Shared service clients and models
│       ├── TmsGatewayApi/
│       │   ├── ITmsGatewayClient.cs         # Gateway client interface
│       │   ├── TmsGatewayClient.cs          # HTTP client that posts shipments to the gateway
│       │   ├── Configuration/
│       │   │   └── TmsGatewayConfiguration.cs
│       │   └── Model/                       # Gateway resource models (Shipment, Stop, Unit, etc.)
│       ├── AccessToken/
│       │   ├── IAccessTokenClient.cs        # Access token client interface
│       │   ├── AccessTokenClient.cs         # OIDC authorization-code + PKCE token acquisition
│       │   └── Configuration/
│       │       └── AccessTokenConfiguration.cs
│       ├── MockApi/
│       │   ├── IMockClient.cs               # Mock data client interface
│       │   ├── MockClient.cs                # Reads orders/addresses from local JSON files
│       │   ├── Orders.json                  # Sample order data
│       │   ├── ShipTo.json                  # Sample ship-to address
│       │   ├── SourceLocation.json          # Sample source/origin address
│       │   └── Model/
│       │       ├── Order.cs
│       │       └── Address.cs
│       └── Extensions/
│           ├── ServiceCollectionExtensions.cs# DI registration for clients and serializer options
│           └── Helpers.cs                   # Random string and PKCE code-challenge utilities
│
└── test/
    └── TmsIntegrationExample.UnitTest       # xUnit tests for transformers
        └── Mock/Models/Transformers/
            ├── MockOrderToShipmentTests.cs
            └── MockAddressToGatewayStopTests.cs
```

### Key Projects

| Project | Description |
|---|---|
| **TmsIntegrationExample.Example** | ASP.NET Core hosted service that runs a one-shot background job to process mock orders and post them as shipments to the TMS Gateway. |
| **TmsIntegrationExample.Services** | Class library containing the TMS Gateway HTTP client, the OIDC access-token client, mock data readers, and all shared models. |
| **TmsIntegrationExample.UnitTest** | xUnit test project with FluentAssertions and Moq for verifying transformer logic. |

## Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/eShippingTechnologies/tms-integration-example.git
   cd tms-integration-example
   ```

2. **Restore dependencies**

   ```bash
   dotnet restore
   ```

3. **Configure credentials** (see [Configuration](#configuration) below)

4. **Build**

   ```bash
   dotnet build
   ```

5. **Run**

   ```bash
   dotnet run --project src/TmsIntegrationExample.Example
   ```

   The application starts as a hosted service, processes the mock orders once, and then exits.

## Configuration

Application settings are in `src/TmsIntegrationExample.Example/appsettings.json`. Sensitive values should be provided via [User Secrets](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets) or environment variables — do not commit credentials to the repository.

### Setting Up User Secrets

```bash
cd src/TmsIntegrationExample.Example
dotnet user-secrets set "Endpoints:TmsGatewayAPI:AccountNumber" "<your-account-number>"
dotnet user-secrets set "Endpoints:AccessTokenAPI:Email" "<your-email>"
dotnet user-secrets set "Endpoints:AccessTokenAPI:Password" "<your-password>"
dotnet user-secrets set "Endpoints:AccessTokenAPI:Scope" "<your-scope>"
```

### Configuration Reference

| Setting | Description |
|---|---|
| `Endpoints:TmsGatewayAPI:BaseAddress` | Base URL of the TMS Gateway (default: staging). |
| `Endpoints:TmsGatewayAPI:ShipmentsSubPath` | API path for shipment operations (default: `shipments`). |
| `Endpoints:TmsGatewayAPI:AccountNumber` | Your TMS account number. |
| `Endpoints:AccessTokenAPI:BaseAddress` | Base URL of the identity provider / login endpoint. |
| `Endpoints:AccessTokenAPI:ClientId` | OAuth client identifier (default: `ui`). |
| `Endpoints:AccessTokenAPI:LoginSubPath` | Path used to authenticate the user session. |
| `Endpoints:AccessTokenAPI:Email` | Login email address. |
| `Endpoints:AccessTokenAPI:Password` | Login password. |
| `Endpoints:AccessTokenAPI:RedirectUri` | OAuth redirect URI. |
| `Endpoints:AccessTokenAPI:Scope` | Requested OAuth scope. |

## How It Works

1. **Startup** — `Program.cs` builds a generic host with `Startup` which registers the background job, the TMS Gateway client, the access-token client, and the mock data reader.

2. **Job Execution** — `TmsIntegrationExampleJob` (a `BackgroundService`) creates a DI scope and calls `TmsIntegrationExampleProcessor.ProcessAsync()`.

3. **Data Loading** — The processor reads mock order data from `Orders.json` and address data from `SourceLocation.json` / `ShipTo.json` via the `MockClient`. In a real integration these would be replaced by calls to your ERP or order management system.

4. **Transformation** — Each order is transformed into a `ShipmentPost` using:
   - `MockOrderToShipment` — maps order fields (order number, PO number, requested date) and sets reference numbers (`SO_NUMBER`, `PO_NUMBER`, `SHIPMENT_ID`).
   - `MockAddressToGatewayStop` — maps physical/mailing address fields to a gateway `Stop`, normalizing phone numbers and country codes.

5. **Authentication** — `AccessTokenClient` performs an OpenID Connect authorization-code flow with PKCE against the identity provider to obtain a bearer token.

6. **Shipment Posting** — `TmsGatewayClient` attaches the bearer token and POSTs the serialized `ShipmentPost` to the TMS Gateway's shipments endpoint. The gateway returns a full `Shipment` resource with a `ShipmentId`.

### Key Models

| Model | Purpose |
|---|---|
| `ShipmentPost` | Request body for creating a shipment (status, origin/destination stops, units, reference numbers, billing, etc.). |
| `Shipment` | Full shipment resource returned by the gateway, including the assigned `ShipmentId`. |
| `Stop` | Origin or destination location with address, contact, and scheduling details. |
| `Unit` | Individual handling unit (freight class, weight, dimensions, hazmat properties). |
| `ReferenceNumber` | Key-value pair for customer-specific identifiers (SO number, PO number, etc.). |
| `BookingOptions` | Carrier selection, service level, and dispatch preferences for booking. |
| `BillingDetailPost` | Billing party and address information for the shipment. |

## Running Tests

```bash
dotnet test
```

Tests are located in `test/TmsIntegrationExample.UnitTest` and cover the transformer logic:

- **MockOrderToShipmentTests** — verifies that orders are correctly mapped to `ShipmentPost` resources, including reference number assembly.
- **MockAddressToGatewayStopTests** — verifies that addresses are correctly mapped to `Stop` resources, including phone formatting and country code normalization.

## Postman Collection

A Postman collection is included in the `postman-example/` directory with sample requests for interacting with the TMS Gateway API directly. Import `TMS Gateway Examples.postman_collection.json` into Postman to explore the available endpoints.
