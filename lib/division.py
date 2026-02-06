"""Division management for VWork.

Provides read-only queries over division configuration, employee rosters,
project listings, and heartbeat status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import CompanyConfig, DivisionConfig, EmployeeConfig, ProjectRef


@dataclass(slots=True)
class DivisionStatus:
    """Snapshot of a division's operational state."""

    id: str
    name: str
    name_cn: str
    description: str
    director: str
    path: Path
    employees: list[EmployeeConfig]
    projects: list[ProjectRef]
    heartbeat: str  # raw content of HEARTBEAT.md or a default message
    has_heartbeat: bool


class DivisionManager:
    """High-level queries for VWork divisions.

    Usage::

        cfg = CompanyConfig()
        dm = DivisionManager(cfg)

        for div in dm.list_divisions():
            print(div.name, len(div.employees), "employees")

        status = dm.get_status("content-studio")
        print(status.heartbeat)
    """

    def __init__(self, config: CompanyConfig) -> None:
        self._cfg = config

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_divisions(self) -> list[DivisionStatus]:
        """Return a status snapshot for every registered division."""
        return [
            self._build_status(div_id)
            for div_id in self._cfg.divisions
        ]

    def get_division(self, division_id: str) -> DivisionConfig:
        """Return raw division config.  Raises ``KeyError`` if not found."""
        return self._cfg.division(division_id)

    def get_status(self, division_id: str) -> DivisionStatus:
        """Return a full status snapshot for a single division."""
        return self._build_status(division_id)

    def get_employees(self, division_id: str) -> list[EmployeeConfig]:
        """Return all employees in a division."""
        return self._cfg.employees_in_division(division_id)

    def get_projects(self, division_id: str) -> list[ProjectRef]:
        """Return all project references for a division."""
        div = self._cfg.division(division_id)
        return list(div.projects)

    def get_heartbeat(self, division_id: str) -> str:
        """Read and return the raw HEARTBEAT.md content (or a default)."""
        heartbeat_path = self._heartbeat_path(division_id)
        if heartbeat_path.exists():
            return heartbeat_path.read_text(encoding="utf-8")
        return f"No HEARTBEAT.md found for division '{division_id}'."

    def has_heartbeat(self, division_id: str) -> bool:
        """Return whether a HEARTBEAT.md file exists for the division."""
        return self._heartbeat_path(division_id).exists()

    def get_director(self, division_id: str) -> EmployeeConfig | None:
        """Return the director employee config, or ``None`` if unset."""
        div = self._cfg.division(division_id)
        if not div.director:
            return None
        try:
            return self._cfg.employee(div.director)
        except KeyError:
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _division_abs_path(self, division_id: str) -> Path:
        return self._cfg.division_path(division_id)

    def _heartbeat_path(self, division_id: str) -> Path:
        return self._division_abs_path(division_id) / "HEARTBEAT.md"

    def _build_status(self, division_id: str) -> DivisionStatus:
        div = self._cfg.division(division_id)
        employees = self._cfg.employees_in_division(division_id)
        hb_path = self._heartbeat_path(division_id)
        hb_exists = hb_path.exists()
        heartbeat = (
            hb_path.read_text(encoding="utf-8")
            if hb_exists
            else f"No HEARTBEAT.md for '{division_id}'."
        )
        return DivisionStatus(
            id=div.id,
            name=div.name,
            name_cn=div.name_cn,
            description=div.description,
            director=div.director,
            path=self._division_abs_path(division_id),
            employees=employees,
            projects=list(div.projects),
            heartbeat=heartbeat,
            has_heartbeat=hb_exists,
        )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"DivisionManager(divisions={len(self._cfg.divisions)})"
