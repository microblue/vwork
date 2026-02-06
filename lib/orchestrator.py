"""Multi-agent task orchestrator for VWork.

Manages the task board (``board/active.yaml``, ``board/archive/``),
assigns work to employees, and collects division status for daily standups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from .config import CompanyConfig, EmployeeConfig
from .division import DivisionManager


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

VALID_STATUSES = frozenset({"active", "completed", "blocked"})


@dataclass(slots=True)
class Task:
    """A single task on the board."""

    id: str
    title: str
    assignee: str
    status: str
    created: str
    division: str
    description: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "title": self.title,
            "assignee": self.assignee,
            "status": self.status,
            "created": self.created,
            "division": self.division,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            id=str(data["id"]),
            title=str(data.get("title", "")),
            assignee=str(data.get("assignee", "")),
            status=str(data.get("status", "active")),
            created=str(data.get("created", "")),
            division=str(data.get("division", "")),
            description=str(data.get("description", "")),
        )


@dataclass(slots=True)
class StandupEntry:
    """Status report for one division during a daily standup."""

    division_id: str
    division_name: str
    director: str
    employee_count: int
    active_tasks: list[Task]
    heartbeat_summary: str


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class Orchestrator:
    """Coordinate tasks across VWork divisions and employees.

    Usage::

        cfg = CompanyConfig()
        orch = Orchestrator(cfg)

        # Create and assign
        task = orch.create_task(
            title="Review fuxi EP002 script",
            assignee="director-chen",
            division="content-studio",
            description="Full review of dialogue and pacing.",
        )

        # Query
        for t in orch.list_tasks():
            print(t.id, t.title, t.status)

        # Complete
        orch.complete_task(task.id)

        # Standup
        report = orch.daily_standup()
    """

    def __init__(self, config: CompanyConfig) -> None:
        self._cfg = config
        self._board_dir: Path = config.paths.board
        self._active_path: Path = self._board_dir / "active.yaml"
        self._archive_dir: Path = self._board_dir / "archive"
        self._archive_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Task creation
    # ------------------------------------------------------------------

    def create_task(
        self,
        *,
        title: str,
        assignee: str,
        division: str,
        description: str = "",
        status: str = "active",
    ) -> Task:
        """Create a new task and append it to ``board/active.yaml``.

        The task ID is generated as ``YYYY-MM-DD-NNN`` where NNN is a
        zero-padded sequence number for today.
        """
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of {VALID_STATUSES}."
            )
        # Validate assignee and division exist
        self._cfg.employee(assignee)
        self._cfg.division(division)

        today = date.today().isoformat()
        task_id = self._next_task_id(today)

        task = Task(
            id=task_id,
            title=title,
            assignee=assignee,
            status=status,
            created=today,
            division=division,
            description=description,
        )

        tasks = self._load_active_tasks()
        tasks.append(task)
        self._save_active_tasks(tasks)
        return task

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    def assign_task(self, task_id: str, assignee: str) -> Task:
        """Reassign an existing active task to a different employee."""
        self._cfg.employee(assignee)  # validate
        tasks = self._load_active_tasks()
        task = self._find_task(tasks, task_id)
        task.assignee = assignee
        self._save_active_tasks(tasks)
        return task

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_tasks(
        self,
        *,
        status: str | None = None,
        assignee: str | None = None,
        division: str | None = None,
    ) -> list[Task]:
        """Return active tasks, optionally filtered."""
        tasks = self._load_active_tasks()
        if status:
            tasks = [t for t in tasks if t.status == status]
        if assignee:
            tasks = [t for t in tasks if t.assignee == assignee]
        if division:
            tasks = [t for t in tasks if t.division == division]
        return tasks

    def get_task(self, task_id: str) -> Task:
        """Return a single active task by ID."""
        tasks = self._load_active_tasks()
        return self._find_task(tasks, task_id)

    # ------------------------------------------------------------------
    # Completion / archival
    # ------------------------------------------------------------------

    def complete_task(self, task_id: str) -> Task:
        """Mark a task as completed and move it from active to archive.

        The task is written to ``board/archive/YYYY-MM.yaml`` (grouped by
        month) and removed from ``board/active.yaml``.
        """
        tasks = self._load_active_tasks()
        task = self._find_task(tasks, task_id)
        task.status = "completed"

        # Remove from active
        tasks = [t for t in tasks if t.id != task_id]
        self._save_active_tasks(tasks)

        # Append to monthly archive
        self._archive_task(task)
        return task

    # ------------------------------------------------------------------
    # Status updates
    # ------------------------------------------------------------------

    def set_status(self, task_id: str, status: str) -> Task:
        """Update the status of an active task (active / blocked)."""
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of {VALID_STATUSES}."
            )
        if status == "completed":
            return self.complete_task(task_id)

        tasks = self._load_active_tasks()
        task = self._find_task(tasks, task_id)
        task.status = status
        self._save_active_tasks(tasks)
        return task

    # ------------------------------------------------------------------
    # Daily standup
    # ------------------------------------------------------------------

    def daily_standup(self) -> list[StandupEntry]:
        """Collect status from every division for a standup report.

        For each division this gathers:
          - the employee roster
          - active tasks assigned to that division
          - a trimmed heartbeat summary (first 500 chars)
        """
        dm = DivisionManager(self._cfg)
        all_tasks = self._load_active_tasks()
        entries: list[StandupEntry] = []

        for div_id, div_cfg in self._cfg.divisions.items():
            div_tasks = [t for t in all_tasks if t.division == div_id]
            employees = self._cfg.employees_in_division(div_id)
            heartbeat = dm.get_heartbeat(div_id)
            # Trim to a reasonable summary length
            summary = heartbeat[:500].rstrip()
            if len(heartbeat) > 500:
                summary += "\n..."

            director_name = ""
            director_emp = dm.get_director(div_id)
            if director_emp is not None:
                director_name = director_emp.name

            entries.append(
                StandupEntry(
                    division_id=div_id,
                    division_name=div_cfg.name,
                    director=director_name,
                    employee_count=len(employees),
                    active_tasks=div_tasks,
                    heartbeat_summary=summary,
                )
            )

        return entries

    def format_standup(self, entries: list[StandupEntry] | None = None) -> str:
        """Return a Markdown-formatted daily standup report."""
        if entries is None:
            entries = self.daily_standup()

        today = date.today().isoformat()
        lines: list[str] = [
            f"# VWork Daily Standup -- {today}",
            "",
        ]

        for entry in entries:
            lines.append(f"## {entry.division_name}")
            lines.append(f"- Director: {entry.director or '(none)'}")
            lines.append(f"- Employees: {entry.employee_count}")
            lines.append(f"- Active tasks: {len(entry.active_tasks)}")

            if entry.active_tasks:
                lines.append("")
                lines.append("### Tasks")
                for t in entry.active_tasks:
                    lines.append(
                        f"- [{t.status}] **{t.title}** (-> {t.assignee})"
                    )

            lines.append("")
            lines.append("### Heartbeat")
            # Indent the heartbeat content for readability
            for hb_line in entry.heartbeat_summary.splitlines():
                lines.append(f"> {hb_line}")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal: YAML persistence
    # ------------------------------------------------------------------

    def _load_active_tasks(self) -> list[Task]:
        data = _load_yaml(self._active_path)
        raw_tasks = data.get("tasks") or []
        return [Task.from_dict(t) for t in raw_tasks if isinstance(t, dict)]

    def _save_active_tasks(self, tasks: list[Task]) -> None:
        data = {
            "tasks": [t.to_dict() for t in tasks],
        }
        _save_yaml(self._active_path, data, header="# Active Tasks -- currently in progress or assigned")

    def _archive_task(self, task: Task) -> None:
        """Append a completed task to the monthly archive file."""
        # Determine month bucket from creation date or today
        try:
            month_key = task.created[:7]  # "YYYY-MM"
        except (IndexError, TypeError):
            month_key = date.today().strftime("%Y-%m")

        archive_path = self._archive_dir / f"{month_key}.yaml"
        data = _load_yaml(archive_path) if archive_path.exists() else {}
        archived: list[dict] = data.get("tasks", []) or []
        archived.append(task.to_dict())
        data["tasks"] = archived
        _save_yaml(archive_path, data, header=f"# Archived Tasks -- {month_key}")

    # ------------------------------------------------------------------
    # Internal: task ID generation
    # ------------------------------------------------------------------

    def _next_task_id(self, today_iso: str) -> str:
        """Generate the next sequential task ID for *today_iso*.

        Format: ``YYYY-MM-DD-NNN`` (e.g. ``2026-02-02-001``).
        """
        tasks = self._load_active_tasks()
        # Also peek into today's archive to avoid collisions
        month_key = today_iso[:7]
        archive_path = self._archive_dir / f"{month_key}.yaml"
        archive_tasks: list[Task] = []
        if archive_path.exists():
            adat = _load_yaml(archive_path)
            archive_tasks = [
                Task.from_dict(t)
                for t in (adat.get("tasks") or [])
                if isinstance(t, dict)
            ]

        existing_ids = {t.id for t in tasks} | {t.id for t in archive_tasks}
        seq = 1
        while True:
            candidate = f"{today_iso}-{seq:03d}"
            if candidate not in existing_ids:
                return candidate
            seq += 1

    # ------------------------------------------------------------------
    # Internal: lookup helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_task(tasks: list[Task], task_id: str) -> Task:
        for t in tasks:
            if t.id == task_id:
                return t
        raise KeyError(f"Task '{task_id}' not found in active tasks")

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        count = len(self._load_active_tasks())
        return f"Orchestrator(active_tasks={count})"


# ---------------------------------------------------------------------------
# Module-level YAML utilities
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _save_yaml(path: Path, data: dict, *, header: str = "") -> None:
    with path.open("w", encoding="utf-8") as fh:
        if header:
            fh.write(header + "\n")
        yaml.dump(
            data,
            fh,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
