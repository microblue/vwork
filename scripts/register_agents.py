"""Batch-register VWork employees as OpenClaw agents.

Iterates over all employees (or a single one) and calls
``clawdbot agents add`` for each.

Usage::

    python scripts/register_agents.py               # all employees
    python scripts/register_agents.py --employee director-chen  # single
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the vwork root is on sys.path so ``import lib`` works.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import click
from rich.console import Console
from rich.table import Table

from lib import CompanyConfig, OpenClawGateway


console = Console()


@click.command()
@click.option(
    "--employee",
    "employee_id",
    default=None,
    help="Register a single employee by ID. Omit to register all.",
)
def main(employee_id: str | None) -> None:
    """Register VWork employees as OpenClaw agents."""
    try:
        cfg = CompanyConfig()
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    gw = OpenClawGateway(cfg)

    # Determine which employees to register
    if employee_id is not None:
        if employee_id not in cfg.employees:
            console.print(
                f"[red]Error:[/red] Unknown employee '{employee_id}'."
            )
            raise SystemExit(1)
        targets = [employee_id]
    else:
        targets = list(cfg.employees.keys())

    if not targets:
        console.print("[yellow]No employees found to register.[/yellow]")
        return

    console.print(
        f"Registering [bold]{len(targets)}[/bold] employee(s) as "
        f"OpenClaw agents...\n"
    )

    # Results table
    results_table = Table(
        title="Agent Registration Results",
        show_header=True,
        header_style="bold cyan",
        expand=True,
        padding=(0, 1),
    )
    results_table.add_column("Employee", style="bold", min_width=20)
    results_table.add_column("Agent ID", min_width=24)
    results_table.add_column("Status", min_width=10)
    results_table.add_column("Details", ratio=1)

    success_count = 0
    fail_count = 0

    for eid in targets:
        emp = cfg.employee(eid)
        console.print(f"  Registering [bold]{eid}[/bold] ({emp.agent_id})...")

        result = gw.register_agent(eid)

        if result.ok:
            success_count += 1
            status_display = "[green]OK[/green]"
            details = result.stdout.strip() or "(registered)"
        else:
            fail_count += 1
            status_display = f"[red]FAIL ({result.returncode})[/red]"
            details = (
                result.stderr.strip() or result.stdout.strip() or "(no output)"
            )

        results_table.add_row(
            f"{emp.emoji} {emp.name} ({eid})".strip(),
            emp.agent_id,
            status_display,
            details,
        )

    # Print results
    console.print()
    console.print(results_table)

    # Summary line
    console.print()
    summary_parts: list[str] = []
    if success_count:
        summary_parts.append(f"[green]{success_count} succeeded[/green]")
    if fail_count:
        summary_parts.append(f"[red]{fail_count} failed[/red]")
    console.print(f"Done: {', '.join(summary_parts)}.")


if __name__ == "__main__":
    main()
