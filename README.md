# eShipping TMS Integration Examples

This repository contains reference implementations and examples for integrating with the **eShipping TMS Gateway API**.

The examples are intended to help developers understand authentication, shipment creation and management, quoting, booking, tracking, reference numbers, documents, and other common TMS integration workflows.

> **Note:** This repository is provided as a public, read-only mirror of the approved integration examples maintained by eShipping. Changes made directly to this repository may be overwritten during synchronization.

## Available Examples

### C# / .NET

[`C#-example`](./C%23-example/README.md)

A .NET reference application demonstrating a complete TMS Gateway integration, including:

* OAuth/OpenID Connect authentication using PKCE

* Reading and transforming source order data

* Creating shipments

* Shipment, stop, unit, and reference-number models

* TMS Gateway API client implementation

* Dependency injection and configuration

* Unit tests

This example is a good starting point for developers building a production integration using **C# and .NET**.

---

### Python

[`Python-example`](./Python-example/README.md)

A Python client library and interactive console application for working with the TMS Gateway API.

Examples include:

* Authentication using OAuth2 authorization code + PKCE

* Creating and updating shipments

* Retrieving shipments

* Quick quotes

* Shipment quotes

* Booking shipments

* Tracking

* Reference-number management

* Carrier and organization lookups

* Shipment documents

The Python example can also be used as a command-line tool for experimenting with the API before incorporating the client into another application.

---

### Postman

[`postman-example`](./postman-example/README.md)

A Postman collection containing ready-to-run examples of TMS Gateway API requests.

The collection includes examples for:

* Authentication

* Shipment creation

* Shipment updates

* Shipment retrieval

* Shipment cancellation

* Multi-stop shipments

* Shipment searches

* Reference numbers

* Quick quotes

* Booking

* Tracking

* Carrier information

* Organization information

* Shipment documents

The Postman collection is often the easiest place to start when learning the API or troubleshooting an integration.

## Getting Started

Choose the example that best matches how you want to work with the TMS Gateway:

| If you want to...                      | Start here                                     |

| -------------------------------------- | ---------------------------------------------- |

| Explore API calls without writing code | [Postman Example](./Postman-example/README.md) |

| Build a .NET integration               | [C# Example](./C%23-example/README.md)         |

| Build a Python integration             | [Python Example](./Python-example/README.md)   |

Each example directory contains its own README with prerequisites, configuration, authentication, and usage instructions.

## Interactive API Documentation

The eShipping TMS Gateway includes an interactive **Swagger / OpenAPI** page for developers working with the API.

### Staging Swagger

**[Open the TMS Gateway Staging Swagger Page](https://tmsgateway-staging.engagedtechnologies.com/swagger/index.html)**

The Swagger interface can be used to:

* Browse available API endpoints

* Review HTTP methods and routes

* View request parameters

* Inspect request and response models

* Review available data fields and schemas

* See expected response structures and status codes

* Test API requests directly from the browser where supported and properly authenticated

The Swagger documentation is particularly useful when developing or troubleshooting an integration because it provides a direct view of the API contract alongside the C#, Python, and Postman examples in this repository.

### Recommended Development Workflow

For developers new to the TMS Gateway, we recommend:

1. Review the available endpoints in [Swagger](https://tmsgateway-staging.engagedtechnologies.com/swagger/index.html).

2. Use the [Postman Example](./Postman-example/README.md) to experiment with authentication and API requests.

3. Review the [C# Example](./C%23-example/README.md) or [Python Example](./Python-example/README.md) when implementing the integration in application code.

4. Develop and test against the **Staging** environment before moving an integration to Production.

**Note:** The Swagger URL above is for the eShipping TMS Gateway **Staging** environment. Credentials and appropriate access may be required for some operations.

## TMS Gateway Environments

Examples in this repository may support one or more of the following eShipping TMS Gateway environments:

| Environment | Gateway                                              |

| ----------- | ---------------------------------------------------- |

| Staging     | `https://tmsgateway-staging.engagedtechnologies.com` |

| QA          | `https://tmsgateway-qa.engagedtechnologies.com`      |

| Production  | `https://tmsgateway.engagedtechnologies.com`         |

Not every example is configured for every environment. See the README within each example for its supported environment options.

## Authentication

The examples demonstrate OAuth 2.0 / OpenID Connect authentication using **PKCE (Proof Key for Code Exchange)**.

Authentication configuration varies by implementation. Depending on your integration, you may need information supplied by eShipping such as:

* TMS account number

* User or service credentials

* OAuth client ID

* Authorized scopes

* Environment-specific endpoints

See the individual example README for configuration instructions.

## Security

**Do not commit credentials, access tokens, passwords, client secrets, or other sensitive information to your repository.**

Use an appropriate secrets-management mechanism for your development and production environments, such as:

* Environment variables

* .NET User Secrets for local development

* CI/CD secrets

* Azure Key Vault or another production secrets store

The credentials and sample values contained in these examples should not be treated as production credentials.

## Important Notes

These projects are **reference implementations** intended to demonstrate common integration patterns.

They may need to be adapted for your application's:

* Business rules

* Error handling and retry requirements

* Logging and monitoring

* Data transformation

* Authentication model

* Credential management

* Environment configuration

* Production deployment architecture

Developers should review and test integration behavior against the appropriate eShipping environment before deploying changes to production.

## Repository Updates

This public repository is automatically synchronized from the approved `master` branch of eShipping's internal integration-example repository.

As a result:

* `master` represents the currently published examples.

* Internal development and feature branches are not published here.

* Direct changes to this public mirror may be overwritten by a future synchronization.

* Published examples may change as the TMS Gateway and recommended integration patterns evolve.

## Documentation

Detailed documentation for each implementation is located within its respective directory:

* [C# / .NET Documentation](./C%23-example/README.md)

* [Python Documentation](./Python-example/README.md)

* [Postman Documentation](./Postman-example/README.md)

## About eShipping

eShipping provides transportation management technology and services that help organizations manage shipping, carrier connectivity, rating, booking, tracking, and related transportation workflows.

This repository contains technical examples specifically intended to assist developers integrating their systems with the eShipping TMS Gateway.

