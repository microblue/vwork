"""Employee management for VWork.

Handles listing, querying, and provisioning employee workspaces from the
``employees/_template/`` scaffold.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from .config import CompanyConfig, EmployeeConfig, RoleConfig


# Template placeholder tokens (as they appear in the _template/ files).
# Tokens prefixed with "- " are list placeholders that appear on a bullet line
# in the template (e.g. ``- [list of ...]``).  We match the full ``- [...]``
# string so the replacement text can include its own bullets without doubling up.
_PLACEHOLDERS: dict[str, str] = {
    "[employee name]": "{employee_name}",
    "[role title]": "{role_title}",
    "[division name]": "{division_name}",
    "[signature emoji]": "{emoji}",
    "[openclaw agent id]": "{agent_id}",
    "[manager/director name]": "{manager_name}",
    "- [list of key responsibilities]": "{responsibilities}",
    "- [what you're working on right now]": "{current_focus}",
    "- [list of assigned projects]": "{projects}",
    "- [list project paths relevant to your work]": "{project_paths}",
    "- [list tools and how to access them]": "{tools}",
    "- [environment-specific notes]": "{env_notes}",
}

# Template files that get copied into every new employee workspace
_TEMPLATE_FILES = ("AGENTS.md", "SOUL.md", "IDENTITY.md", "ROLE.md", "TOOLS.md")


@dataclass(slots=True)
class EmployeeSummary:
    """Lightweight snapshot of an employee for listing views."""

    id: str
    name: str
    role: str
    division: str
    status: str
    emoji: str
    workspace: Path


class EmployeeManager:
    """High-level operations on VWork employees.

    Usage::

        cfg = CompanyConfig()
        mgr = EmployeeManager(cfg)

        for emp in mgr.list_employees():
            print(emp.name, emp.status)

        mgr.create_employee("sound-designer-echo", division="content-studio",
                            role="sound-designer", name="Echo", ...)
    """

    def __init__(self, config: CompanyConfig) -> None:
        self._cfg = config
        self._template_dir: Path = config.paths.employees / "_template"

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_employees(
        self,
        division: str | None = None,
        status: str | None = None,
    ) -> list[EmployeeSummary]:
        """Return all employees, optionally filtered by division/status."""
        results: list[EmployeeSummary] = []
        for eid, emp in self._cfg.employees.items():
            if division and emp.division != division:
                continue
            if status and emp.status != status:
                continue
            results.append(
                EmployeeSummary(
                    id=eid,
                    name=emp.name,
                    role=emp.role,
                    division=emp.division,
                    status=emp.status,
                    emoji=emp.emoji,
                    workspace=self._cfg.employee_workspace(eid),
                )
            )
        return results

    def get_employee(self, employee_id: str) -> EmployeeConfig:
        """Return the full config for a single employee."""
        return self._cfg.employee(employee_id)

    def get_workspace(self, employee_id: str) -> Path:
        """Return the absolute workspace directory for *employee_id*."""
        return self._cfg.employee_workspace(employee_id)

    def get_role(self, employee_id: str) -> RoleConfig:
        """Return the role config for *employee_id*."""
        emp = self._cfg.employee(employee_id)
        return self._cfg.role(emp.role)

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create_employee(
        self,
        employee_id: str,
        *,
        name: str,
        name_cn: str = "",
        role: str,
        division: str,
        emoji: str = "",
        agent_id: str | None = None,
        current_focus: str = "Onboarding -- getting up to speed",
    ) -> Path:
        """Provision a new employee workspace and register in employees.yaml.

        Steps:
          1. Validate the division and role exist.
          2. Build the workspace directory under the division's employees/ folder.
          3. Copy template files and fill in placeholders.
          4. Create the ``memory/`` subdirectory.
          5. Append the new employee to ``org/employees.yaml``.

        Returns the absolute path to the new workspace.
        """
        if employee_id in self._cfg.employees:
            raise ValueError(f"Employee '{employee_id}' already exists")

        div_cfg = self._cfg.division(division)  # KeyError if missing
        role_cfg = self._cfg.role(role)          # KeyError if missing

        if agent_id is None:
            agent_id = f"vwork-{employee_id}"

        workspace = self._cfg.root / div_cfg.path / "employees" / employee_id

        if workspace.exists():
            raise FileExistsError(f"Workspace already exists: {workspace}")

        # Determine the director / manager for this employee
        manager_name = self._resolve_manager(employee_id, div_cfg.director)

        # Build the replacement map
        responsibilities = "\n".join(
            f"- {r}" for r in role_cfg.responsibilities
        ) if role_cfg.responsibilities else "- (to be defined)"

        projects_text = "\n".join(
            f"- {p.name} ({p.id})" for p in div_cfg.projects
        ) if div_cfg.projects else "- (none assigned yet)"

        project_paths = "\n".join(
            f"- `{p.source}` ({p.name})" for p in div_cfg.projects
        ) if div_cfg.projects else "- (none)"

        replacements: dict[str, str] = {
            "{employee_name}": name,
            "{role_title}": role_cfg.title,
            "{division_name}": div_cfg.name,
            "{emoji}": emoji,
            "{agent_id}": agent_id,
            "{manager_name}": manager_name,
            "{responsibilities}": responsibilities,
            "{current_focus}": f"- {current_focus}",
            "{projects}": projects_text,
            "{project_paths}": project_paths,
            "{tools}": "- clawdbot (OpenClaw agent CLI)",
            "{env_notes}": f"- Division: {div_cfg.name}\n- Role: {role_cfg.title}",
        }

        # 1. Create workspace
        workspace.mkdir(parents=True)
        (workspace / "memory").mkdir()

        # 2. Copy and fill templates
        for filename in _TEMPLATE_FILES:
            src = self._template_dir / filename
            if not src.exists():
                continue
            content = src.read_text(encoding="utf-8")
            content = self._apply_placeholders(content, replacements)
            (workspace / filename).write_text(content, encoding="utf-8")

        # 3. Register in employees.yaml
        rel_path = f"{div_cfg.path}/employees/{employee_id}"
        self._register_employee(
            employee_id=employee_id,
            name=name,
            name_cn=name_cn,
            agent_id=agent_id,
            role=role,
            division=division,
            path=rel_path,
            emoji=emoji,
        )

        # Reload config so the new employee is immediately visible
        self._cfg = CompanyConfig(self._cfg.root)

        return workspace

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_manager(self, employee_id: str, director_id: str) -> str:
        """Return the human-readable manager name for a new employee."""
        if employee_id == director_id:
            return "Dawson (Founder)"
        try:
            director = self._cfg.employee(director_id)
            return director.name
        except KeyError:
            return "Dawson (Founder)"

    @staticmethod
    def _apply_placeholders(
        content: str,
        replacements: dict[str, str],
    ) -> str:
        """Two-pass replacement: first raw bracket tokens, then format keys."""
        # Pass 1 -- replace the literal bracket placeholders with format keys
        for raw_token, fmt_key in _PLACEHOLDERS.items():
            content = content.replace(raw_token, fmt_key)
        # Pass 2 -- fill the format keys with actual values
        for key, value in replacements.items():
            content = content.replace(key, value)
        return content

    def _register_employee(
        self,
        *,
        employee_id: str,
        name: str,
        name_cn: str,
        agent_id: str,
        role: str,
        division: str,
        path: str,
        emoji: str,
    ) -> None:
        """Append a new employee entry to ``org/employees.yaml``."""
        yaml_path = self._cfg.paths.org / "employees.yaml"
        data = _load_yaml(yaml_path)

        employees: dict = data.setdefault("employees", {})
        employees[employee_id] = {
            "name": name,
            "name_cn": name_cn,
            "agent_id": agent_id,
            "role": role,
            "division": division,
            "path": path,
            "emoji": emoji,
            "status": "active",
        }

        _save_yaml(yaml_path, data)


# ---------------------------------------------------------------------------
# Module-level YAML utilities
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _save_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(
            data,
            fh,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
