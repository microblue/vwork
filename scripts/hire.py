"""Hire a new employee into the VWork virtual company.

Creates the employee workspace from the template, registers them in
employees.yaml, and optionally registers the corresponding OpenClaw agent.

Usage::

    python scripts/hire.py --name Echo --id sound-designer-echo \\
        --role sound-designer --division content-studio

    python scripts/hire.py --name Echo --id sound-designer-echo \\
        --role sound-designer --division content-studio \\
        --emoji "🔊" --no-register
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

from lib import CompanyConfig, EmployeeManager, OpenClawGateway


console = Console()


@click.command()
@click.option(
    "--name",
    required=True,
    help="Employee display name (e.g. 'Echo').",
)
@click.option(
    "--id",
    "employee_id",
    required=True,
    help="Employee ID slug (e.g. 'sound-designer-echo').",
)
@click.option(
    "--role",
    required=True,
    help="Role ID from roles.yaml (e.g. 'sound-designer').",
)
@click.option(
    "--division",
    required=True,
    help="Division ID (e.g. 'content-studio').",
)
@click.option(
    "--emoji",
    default="",
    help="Optional signature emoji for the employee.",
)
@click.option(
    "--register/--no-register",
    default=True,
    show_default=True,
    help="Also register employee as an OpenClaw agent.",
)
def main(
    name: str,
    employee_id: str,
    role: str,
    division: str,
    emoji: str,
    register: bool,
) -> None:
    """Create a new VWork employee and provision their workspace."""
    try:
        cfg = CompanyConfig()
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    mgr = EmployeeManager(cfg)

    # -- Validate inputs early ----------------------------------------
    if division not in cfg.divisions:
        console.print(f"[red]Error:[/red] Unknown division '{division}'.")
        console.print(
            f"Available divisions: {', '.join(cfg.divisions.keys())}"
        )
        raise SystemExit(1)

    if role not in cfg.roles:
        console.print(f"[red]Error:[/red] Unknown role '{role}'.")
        console.print(f"Available roles: {', '.join(cfg.roles.keys())}")
        raise SystemExit(1)

    if employee_id in cfg.employees:
        console.print(
            f"[red]Error:[/red] Employee '{employee_id}' already exists."
        )
        raise SystemExit(1)

    # -- Create the employee ------------------------------------------
    console.print(f"Creating employee [bold]{name}[/bold] ({employee_id})...")

    try:
        workspace = mgr.create_employee(
            employee_id,
            name=name,
            role=role,
            division=division,
            emoji=emoji,
        )
    except (ValueError, FileExistsError, KeyError) as exc:
        console.print(f"[red]Error creating employee:[/red] {exc}")
        raise SystemExit(1)

    # -- Success summary ----------------------------------------------
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")
    info_table.add_row("Name", name)
    info_table.add_row("ID", employee_id)
    info_table.add_row("Role", role)
    info_table.add_row("Division", division)
    info_table.add_row("Workspace", str(workspace))
    if emoji:
        info_table.add_row("Emoji", emoji)

    console.print()
    console.print(
        Panel(info_table, title="Employee Created", border_style="green")
    )

    # -- Optional agent registration ----------------------------------
    if register:
        console.print()
        console.print("Registering OpenClaw agent...")

        # Reload config so the new employee is visible
        cfg = CompanyConfig()
        gw = OpenClawGateway(cfg)
        result = gw.register_agent(employee_id)

        if result.ok:
            console.print(
                f"[green]Agent registered successfully.[/green]"
            )
            if result.stdout.strip():
                console.print(f"  {result.stdout.strip()}")
        else:
            console.print(
                f"[yellow]Agent registration returned non-zero "
                f"(exit {result.returncode}).[/yellow]"
            )
            if result.stderr.strip():
                console.print(f"  [dim]{result.stderr.strip()}[/dim]")
            if result.stdout.strip():
                console.print(f"  {result.stdout.strip()}")
    else:
        console.print(
            "\n[dim]Skipped agent registration (--no-register).[/dim]"
        )


if __name__ == "__main__":
    main()
