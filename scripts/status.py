"""VWork company status dashboard.

Displays a rich terminal overview of the company: divisions, employees,
projects, heartbeat summaries, and active task counts.

Usage::

    python scripts/status.py
    pixi run status
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
from rich.table import Table
from rich.text import Text

from lib import CompanyConfig, DivisionManager, Orchestrator


console = Console()


def _heartbeat_preview(heartbeat: str, max_lines: int = 3) -> str:
    """Return the first *max_lines* of a heartbeat, trimmed."""
    lines = heartbeat.splitlines()
    preview = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        preview += "\n..."
    return preview


def _build_division_table(cfg: CompanyConfig, dm: DivisionManager) -> Table:
    """Build a rich Table summarising every division."""
    table = Table(
        title="Divisions",
        show_header=True,
        header_style="bold cyan",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Division", style="bold", min_width=18)
    table.add_column("Director", min_width=14)
    table.add_column("Employees", justify="right", min_width=6)
    table.add_column("Projects", justify="right", min_width=6)
    table.add_column("Heartbeat", ratio=1)

    for div_status in dm.list_divisions():
        director_display = div_status.director or "(none)"
        # Try to resolve director name from config
        try:
            director_emp = cfg.employee(div_status.director)
            director_display = f"{director_emp.name} ({director_emp.id})"
        except KeyError:
            pass

        heartbeat_preview = _heartbeat_preview(div_status.heartbeat)

        table.add_row(
            f"{div_status.name}\n[dim]{div_status.name_cn}[/dim]",
            director_display,
            str(len(div_status.employees)),
            str(len(div_status.projects)),
            heartbeat_preview,
        )

    return table


def _build_task_summary(orch: Orchestrator) -> str:
    """Return a one-line task summary string."""
    all_tasks = orch.list_tasks()
    active = [t for t in all_tasks if t.status == "active"]
    blocked = [t for t in all_tasks if t.status == "blocked"]
    parts: list[str] = []
    parts.append(f"{len(all_tasks)} total")
    parts.append(f"{len(active)} active")
    if blocked:
        parts.append(f"{len(blocked)} blocked")
    return ", ".join(parts)


@click.command()
def main() -> None:
    """Display the VWork company status dashboard."""
    try:
        cfg = CompanyConfig()
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    dm = DivisionManager(cfg)
    orch = Orchestrator(cfg)

    # -- Company header ------------------------------------------------
    header_text = Text()
    header_text.append(cfg.company.name, style="bold magenta")
    header_text.append(f" ({cfg.company.name_cn})", style="dim")
    header_text.append(f"\n{cfg.company.tagline}")
    header_text.append(f"\nFounder: {cfg.company.founder}")
    header_text.append(f"  |  Founded: {cfg.company.founded}")
    header_text.append(f"  |  Platform: {cfg.runtime.platform}")
    header_text.append(f"  |  Model: {cfg.runtime.default_model}")

    console.print(Panel(header_text, title="Company Info", border_style="blue"))

    # -- Division table ------------------------------------------------
    console.print()
    console.print(_build_division_table(cfg, dm))

    # -- Task board summary -------------------------------------------
    console.print()
    task_summary = _build_task_summary(orch)
    console.print(
        Panel(
            f"[bold]{task_summary}[/bold]",
            title="Task Board",
            border_style="green",
        )
    )

    # -- Employee roster (compact) ------------------------------------
    console.print()
    emp_table = Table(
        title="All Employees",
        show_header=True,
        header_style="bold yellow",
        expand=True,
        padding=(0, 1),
    )
    emp_table.add_column("ID", style="bold")
    emp_table.add_column("Name")
    emp_table.add_column("Role")
    emp_table.add_column("Division")
    emp_table.add_column("Status")

    for emp in cfg.employees.values():
        status_style = "green" if emp.status == "active" else "red"
        emp_table.add_row(
            emp.id,
            f"{emp.emoji} {emp.name}".strip(),
            emp.role,
            emp.division,
            f"[{status_style}]{emp.status}[/{status_style}]",
        )

    console.print(emp_table)


if __name__ == "__main__":
    main()
