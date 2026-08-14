"""Reusable console prompts and renderers for the TMS Gateway CLI."""

import json
import os
from typing import Any, Callable, Dict, List, Optional, Sequence

from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table

console = Console()


def header(title: str, subtitle: str = "") -> None:
    console.print()
    console.print(Panel.fit(title if not subtitle else f"{title}\n[dim]{subtitle}[/dim]", style="bold cyan"))


def info(message: str) -> None:
    console.print(f"[cyan]{message}[/cyan]")


def success(message: str) -> None:
    console.print(f"[green]{message}[/green]")


def warn(message: str) -> None:
    console.print(f"[yellow]{message}[/yellow]")


def error(message: str) -> None:
    console.print(f"[red]{message}[/red]")


def show_json(payload: Any, title: str = "") -> None:
    text = json.dumps(payload, indent=2, default=str)
    console.print(Panel(JSON(text), title=title or None, border_style="dim"))


def ask(label: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Ask for free text. Returns None when the answer is blank and optional."""
    while True:
        answer = Prompt.ask(label, default=default) if default is not None else Prompt.ask(label, default="")
        answer = (answer or "").strip()
        if answer:
            return answer
        if not required:
            return None
        error("A value is required.")


def ask_int(label: str, default: Optional[int] = None, required: bool = True) -> Optional[int]:
    while True:
        if default is not None:
            return IntPrompt.ask(label, default=default)
        raw = Prompt.ask(label, default="")
        raw = (raw or "").strip()
        if not raw:
            if required:
                error("A whole number is required.")
                continue
            return None
        try:
            return int(raw)
        except ValueError:
            error(f"'{raw}' is not a whole number.")


def ask_decimal(label: str, default: Optional[float] = None, required: bool = True) -> Optional[float]:
    while True:
        if default is not None:
            return FloatPrompt.ask(label, default=default)
        raw = Prompt.ask(label, default="")
        raw = (raw or "").strip()
        if not raw:
            if required:
                error("A number is required.")
                continue
            return None
        try:
            return float(raw)
        except ValueError:
            error(f"'{raw}' is not a number.")


def ask_yes_no(label: str, default: bool = False) -> bool:
    return Confirm.ask(label, default=default)


def ask_choice(
    label: str,
    options: Sequence[str],
    default: Optional[str] = None,
    allow_blank: bool = False,
) -> Optional[str]:
    """Present a numbered pick list and return the chosen value."""
    console.print(f"[bold]{label}[/bold]")
    for index, option in enumerate(options, start=1):
        marker = " [dim](default)[/dim]" if option == default else ""
        console.print(f"  {index}. {option}{marker}")
    hint = "leave blank to skip" if allow_blank and default is None else f"default: {default}" if default else ""
    while True:
        raw = Prompt.ask(f"  Select 1-{len(options)}" + (f" ({hint})" if hint else ""), default="")
        raw = (raw or "").strip()
        if not raw:
            if default is not None:
                return default
            if allow_blank:
                return None
            error("Please pick one of the listed options.")
            continue
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        upper = raw.upper()
        if upper in [option.upper() for option in options]:
            return next(option for option in options if option.upper() == upper)
        error(f"'{raw}' is not one of the listed options.")


def ask_multi_choice(label: str, options: Sequence[str]) -> List[str]:
    """Pick zero or more options, entered as a comma separated list of numbers."""
    console.print(f"[bold]{label}[/bold] [dim](comma separated numbers, blank for none)[/dim]")
    for index, option in enumerate(options, start=1):
        console.print(f"  {index}. {option}")
    while True:
        raw = (Prompt.ask("  Select", default="") or "").strip()
        if not raw:
            return []
        selections = [part.strip() for part in raw.split(",") if part.strip()]
        chosen: List[str] = []
        invalid = [part for part in selections if not (part.isdigit() and 1 <= int(part) <= len(options))]
        if invalid:
            error(f"Invalid selection(s): {', '.join(invalid)}")
            continue
        for part in selections:
            option = options[int(part) - 1]
            if option not in chosen:
                chosen.append(option)
        return chosen


def ask_json(label: str = "JSON body") -> Optional[Dict[str, Any]]:
    """Read a JSON document from a file path or pasted text."""
    source = ask_choice(f"How would you like to supply the {label}?", ["Path to a .json file", "Paste it here"])
    if source == "Path to a .json file":
        path = ask("File path", required=True)
        expanded = os.path.expanduser(path or "")
        if not os.path.isfile(expanded):
            error(f"No file found at {expanded}")
            return None
        with open(expanded, "r", encoding="utf-8") as handle:
            raw = handle.read()
    else:
        console.print(f"[dim]Paste the {label}. Finish with a line containing only END.[/dim]")
        lines: List[str] = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == "END":
                break
            lines.append(line)
        raw = "\n".join(lines)

    if not raw.strip():
        error("No JSON was provided.")
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        error(f"That is not valid JSON: {exc}")
        return None
    if not isinstance(parsed, dict):
        error("The JSON body must be an object.")
        return None
    return parsed


def menu(title: str, options: Sequence[str], back_label: str = "Back") -> Optional[str]:
    """Show a menu and return the selected label, or None for back/exit."""
    console.print()
    console.print(f"[bold cyan]{title}[/bold cyan]")
    for index, option in enumerate(options, start=1):
        console.print(f"  {index}. {option}")
    console.print(f"  0. {back_label}")
    while True:
        raw = (Prompt.ask("Select", default="0") or "").strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        error("Please choose one of the listed numbers.")


def table(title: str, columns: Sequence[str], rows: Sequence[Sequence[Any]]) -> None:
    rendered = Table(title=title, header_style="bold magenta", show_lines=False)
    for column in columns:
        rendered.add_column(column)
    for row in rows:
        rendered.add_row(*["" if cell is None else str(cell) for cell in row])
    console.print(rendered)


def run_guarded(action: Callable[[], Any]) -> Any:
    """Run an action, printing API errors instead of unwinding the whole CLI."""
    from tms_gateway.exceptions import TmsGatewayError

    try:
        return action()
    except TmsGatewayError as exc:
        error(str(exc))
        return None
    except KeyboardInterrupt:
        warn("Cancelled.")
        return None
