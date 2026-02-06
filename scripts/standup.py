"""Daily standup report for VWork.

Collects status from each division -- active tasks, employee headcount,
and heartbeat summaries -- then prints a formatted Markdown report.
Optionally sends the report to the founder via Telegram through OpenClaw.

Usage::

    python scripts/standup.py                          # print all
    python scripts/standup.py --division content-studio # one division
    python scripts/standup.py --send                   # print + send
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the vwork root is on sys.path so ``import lib`` works.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from lib import CompanyConfig, OpenClawGateway, Orchestrator


console = Console()


@click.command()
@click.option(
    "--division",
    "division_id",
    default=None,
    help="Only show a single division's standup. Omit for all.",
)
@click.option(
    "--send/--no-send",
    default=False,
    show_default=True,
    help="Send the report to the founder via Telegram.",
)
def main(division_id: str | None, send: bool) -> None:
    """Generate and display a daily standup report."""
    try:
        cfg = CompanyConfig()
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    # Validate division if specified
    if division_id is not None and division_id not in cfg.divisions:
        console.print(
            f"[red]Error:[/red] Unknown division '{division_id}'."
        )
        console.print(
            f"Available divisions: {', '.join(cfg.divisions.keys())}"
        )
        raise SystemExit(1)

    orch = Orchestrator(cfg)

    # Collect standup entries
    entries = orch.daily_standup()

    # Filter to a single division if requested
    if division_id is not None:
        entries = [e for e in entries if e.division_id == division_id]
        if not entries:
            console.print(
                f"[yellow]No standup data for division "
                f"'{division_id}'.[/yellow]"
            )
            return

    # Format to Markdown
    report = orch.format_standup(entries)

    # Display
    console.print()
    console.print(
        Panel(
            Markdown(report),
            title="Daily Standup",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # Optionally send via Telegram
    if send:
        console.print()
        console.print("Sending standup report to founder via Telegram...")

        gw = OpenClawGateway(cfg)

        # Find a director or ops-manager to relay the message through.
        # We pick the first available employee to act as the sender.
        sender_id = _pick_sender(cfg)
        if sender_id is None:
            console.print(
                "[red]Error:[/red] No active employees found to send through."
            )
            raise SystemExit(1)

        result = gw.send_message(sender_id, report)

        if result.ok:
            console.print(
                f"[green]Report sent successfully "
                f"via {sender_id}.[/green]"
            )
        else:
            console.print(
                f"[red]Failed to send report "
                f"(exit {result.returncode}).[/red]"
            )
            if result.stderr.strip():
                console.print(f"  [dim]{result.stderr.strip()}[/dim]")
    else:
        console.print(
            "\n[dim]Use --send to deliver this report via Telegram.[/dim]"
        )


def _pick_sender(cfg: CompanyConfig) -> str | None:
    """Choose the best employee to act as the Telegram relay.

    Preference order:
      1. ops-manager-sys (operations manager)
      2. any division director
      3. first active employee
    """
    # Prefer the ops manager
    if "ops-manager-sys" in cfg.employees:
        return "ops-manager-sys"

    # Fall back to any director
    for div in cfg.divisions.values():
        if div.director and div.director in cfg.employees:
            return div.director

    # Last resort: first active employee
    for eid, emp in cfg.employees.items():
        if emp.status == "active":
            return eid

    return None


if __name__ == "__main__":
    main()
