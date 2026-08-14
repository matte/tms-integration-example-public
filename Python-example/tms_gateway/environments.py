"""Environment definitions for the TMS Gateway API."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Environment:
    """A named TMS Gateway deployment (gateway + identity server)."""

    name: str
    gateway_base_url: str
    identity_base_url: str


QA = Environment(
    name="qa",
    gateway_base_url="https://tmsgateway-qa.engagedtechnologies.com",
    identity_base_url="https://login.tms-qa.engagedtechnologies.com",
)

STAGING = Environment(
    name="staging",
    gateway_base_url="https://tmsgateway-staging.engagedtechnologies.com",
    identity_base_url="https://login.tms-staging.engagedtechnologies.com",
)

PRODUCTION = Environment(
    name="production",
    gateway_base_url="https://tmsgateway.engagedtechnologies.com",
    identity_base_url="https://login.tms.engagedtechnologies.com",
)

ENVIRONMENTS = {env.name: env for env in (QA, STAGING, PRODUCTION)}

DEFAULT_ENVIRONMENT = STAGING


def get_environment(name: str) -> Environment:
    """Look up an environment by name (qa, staging, production)."""
    key = name.strip().lower()
    if key not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment '{name}'. Valid values: {', '.join(ENVIRONMENTS)}")
    return ENVIRONMENTS[key]
