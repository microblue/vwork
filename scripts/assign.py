"""Assign a task to a VWork employee.

Creates a new task on the board and optionally delivers it via OpenClaw
messaging.

Usage::

    python scripts/assign.py --to director-chen --task "Review EP002 script"

    python scripts/assign.py --to scriptwriter-kai \\
        --task "Write EP003 outline" \\
        --title "EP003 outline" \\
        --deliver
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the vwork root is on sys.path so ``import lib`` works.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lib import CompanyConfig, OpenClawGateway, Orchestrator


console = Console()


def _derive_title(task_description: str, max_length: int = 60) -> str:
    """Derive a short title from a task description.

    Takes the first sentence or first *max_length* characters, whichever
    is shorter.
    """
    # Use the first sentence
    for sep in (".", "!", "?", "\n"):
        idx = task_description.find(sep)
        if 0 < idx < max_length:
            return task_description[:idx].strip()

    # Fall back to truncation
    if len(task_description) <= max_length:
        return task_description.strip()
    return task_description[:max_length].rstrip() + "..."


@click.command()
@click.option(
    "--to",
    "assignee",
    required=True,
    help="Target employee ID (e.g. 'director-chen').",
)
@click.option(
    "--task",
    "task_description",
    required=True,
    help="Full task description.",
)
@click.option(
    "--title",
    default=None,
    help="Short task title. Derived from --task if omitted.",
)
@click.option(
    "--division",
    default=None,
    help="Division ID. Derived from the employee if omitted.",
)
@click.option(
    "--deliver/--no-deliver",
    default=False,
    show_default=True,
    help="Also send the task via OpenClaw message.",
)
def main(
    assignee: str,
    task_description: str,
    title: str | None,
    division: str | None,
    deliver: bool,
) -> None:
    """Create a task and assign it to a VWork employee."""
    try:
        cfg = CompanyConfig()
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    # -- Validate assignee --------------------------------------------
    if assignee not in cfg.employees:
        console.print(f"[red]Error:[/red] Unknown employee '{assignee}'.")
        console.print(
            f"Available employees: {', '.join(cfg.employees.keys())}"
        )
        raise SystemExit(1)

    emp = cfg.employee(assignee)

    # -- Resolve division ---------------------------------------------
    if division is None:
        division = emp.division

    if division not in cfg.divisions:
        console.print(f"[red]Error:[/red] Unknown division '{division}'.")
        raise SystemExit(1)

    # -- Resolve title ------------------------------------------------
    if title is None:
        title = _derive_title(task_description)

    # -- Create the task on the board ---------------------------------
    orch = Orchestrator(cfg)

    try:
        task = orch.create_task(
            title=title,
            assignee=assignee,
            division=division,
            description=task_description,
        )
    except (ValueError, KeyError) as exc:
        console.print(f"[red]Error creating task:[/red] {exc}")
        raise SystemExit(1)

    # -- Display result -----------------------------------------------
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")
    info_table.add_row("Task ID", task.id)
    info_table.add_row("Title", task.title)
    info_table.add_row("Assignee", f"{emp.emoji} {emp.name} ({assignee})")
    info_table.add_row("Division", division)
    info_table.add_row("Status", task.status)
    info_table.add_row("Description", task.description)

    console.print()
    console.print(
        Panel(info_table, title="Task Created", border_style="green")
    )

    # -- Optional delivery via OpenClaw -------------------------------
    if deliver:
        console.print()
        console.print(
            f"Delivering task to [bold]{assignee}[/bold] via OpenClaw..."
        )

        gw = OpenClawGateway(cfg)
        message = (
            f"New task assigned: {task.title}\n\n"
            f"ID: {task.id}\n"
            f"Description: {task.description}"
        )
        result = gw.send_message(assignee, message)

        if result.ok:
            console.print("[green]Task delivered successfully.[/green]")
            if result.stdout.strip():
                console.print(f"  {result.stdout.strip()}")
        else:
            console.print(
                f"[yellow]Delivery returned non-zero "
                f"(exit {result.returncode}).[/yellow]"
            )
            if result.stderr.strip():
                console.print(f"  [dim]{result.stderr.strip()}[/dim]")
    else:
        console.print(
            "\n[dim]Use --deliver to send this task via OpenClaw.[/dim]"
        )


if __name__ == "__main__":
    main()
