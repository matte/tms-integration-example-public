"""Interactive TMS Gateway console.

Authenticates once with PKCE, keeps the token in memory for the session and
renews it automatically whenever it expires.
"""

import argparse
import getpass
import os
import sys
from typing import Optional

from tms_gateway import TmsGatewayClient, get_environment
from tms_gateway.auth import (
    DEFAULT_CLIENT_ID,
    DEFAULT_REDIRECT_URI,
    DEFAULT_SCOPES,
    HeadlessPkceAuthenticator,
    PkceAuthenticator,
)
from tms_gateway.exceptions import AuthenticationError

from . import prompts
from .quotes import quick_quote_flow
from .shipments import create_shipment_flow, find_shipments_flow, open_shipment_flow
from .tracking import track_flow


def build_client(args: argparse.Namespace) -> TmsGatewayClient:
    environment = get_environment(args.environment)
    scopes = args.scope or list(DEFAULT_SCOPES)

    if args.browser_login:
        authenticator = PkceAuthenticator(
            environment=environment,
            client_id=args.client_id,
            redirect_uri=args.redirect_uri,
            scopes=scopes,
            open_browser=not args.no_browser,
            prompt_url=_print_authorize_url,
        )
    else:
        # Headless PKCE: sign in, then take the code from the Location header.
        username = args.username or os.environ.get("TMS_USERNAME") or prompts.ask(
            f"{environment.name} username", required=True
        )
        password = os.environ.get("TMS_PASSWORD") or getpass.getpass(f"{environment.name} password: ")
        authenticator = HeadlessPkceAuthenticator(
            username=username,
            password=password,
            environment=environment,
            client_id=args.client_id,
            redirect_uri=args.redirect_uri,
            scopes=scopes,
        )

    return TmsGatewayClient(authenticator=authenticator, environment=environment)


def _print_authorize_url(url: str) -> None:
    prompts.info("Opening the identity server for sign in. If the browser does not open, use this url:")
    prompts.console.print(url, style="dim")


def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    client = build_client(args)

    prompts.header(
        "TMS Gateway console",
        f"environment {client.environment.name} | gateway {client.base_url}",
    )

    try:
        client.login()
    except AuthenticationError as error:
        prompts.error(str(error))
        return 1

    token = client.authenticator.token
    if token:
        prompts.success(f"Signed in. Token valid for {int(token.seconds_remaining / 60)} minutes.")

    while True:
        choice = prompts.menu(
            "Main menu",
            ["Create shipment", "Quick quote", "Track", "Open a shipment by id", "Find shipments", "Sign in again"],
            back_label="Exit",
        )
        if choice is None:
            prompts.info("Goodbye.")
            return 0

        if choice == "Create shipment":
            create_shipment_flow(client)
        elif choice == "Quick quote":
            quick_quote_flow(client)
        elif choice == "Track":
            track_flow(client)
        elif choice == "Open a shipment by id":
            open_shipment_flow(client)
        elif choice == "Find shipments":
            find_shipments_flow(client)
        elif choice == "Sign in again":
            client.authenticator.invalidate()
            try:
                client.login()
                prompts.success("Signed in again.")
            except AuthenticationError as error:
                prompts.error(str(error))


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive client for the Engaged Technologies TMS Gateway.")
    parser.add_argument(
        "--environment",
        "-e",
        default="staging",
        choices=["qa", "staging", "production"],
        help="Which TMS Gateway deployment to talk to (default: staging).",
    )
    parser.add_argument(
        "--username",
        "-u",
        help="Username for the headless sign in (or set TMS_USERNAME; TMS_PASSWORD for the password).",
    )
    parser.add_argument(
        "--browser-login",
        action="store_true",
        help="Sign in through the browser with a loopback redirect instead of headless PKCE.",
    )
    parser.add_argument("--client-id", default=DEFAULT_CLIENT_ID, help="OAuth client id (default: Sandbox).")
    parser.add_argument(
        "--redirect-uri",
        default=DEFAULT_REDIRECT_URI,
        help="Redirect uri registered for the client (default: http://localhost:5555/auth).",
    )
    parser.add_argument(
        "--scope",
        action="append",
        help="Scope to request; repeat the flag for several scopes.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="With --browser-login, print the authorize url instead of opening a browser.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
