"""YAML configuration loader for the VWork virtual company.

Loads and provides typed access to:
  - company.yaml   (top-level company identity and runtime config)
  - org/divisions.yaml
  - org/roles.yaml
  - org/employees.yaml
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Low-level dataclasses mirroring the YAML structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """Agent runtime settings."""

    platform: str
    default_model: str
    premium_model: str
    max_concurrent_agents: int = 4


@dataclass(frozen=True, slots=True)
class ChannelsConfig:
    """Communication channel settings."""

    primary: str = "telegram"
    internal: str = "filesystem"


@dataclass(frozen=True, slots=True)
class PathsConfig:
    """Resolved filesystem paths used across the project."""

    root: Path
    divisions: Path
    employees: Path
    org: Path
    board: Path
    scripts: Path
    lib: Path

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> PathsConfig:
        return cls(**{k: Path(v) for k, v in data.items()})


@dataclass(frozen=True, slots=True)
class ProjectRef:
    """A lightweight reference to a project inside a division."""

    id: str
    name: str
    type: str
    source: Path


@dataclass(frozen=True, slots=True)
class DivisionConfig:
    """Configuration for a single division."""

    id: str
    name: str
    name_cn: str
    description: str
    director: str
    path: str  # relative path from project root
    projects: list[ProjectRef] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RoleConfig:
    """Configuration for a single role template."""

    id: str
    title: str
    title_cn: str
    level: str
    permissions: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    model: str = ""


@dataclass(frozen=True, slots=True)
class EmployeeConfig:
    """Configuration for a single employee."""

    id: str
    name: str
    name_cn: str
    agent_id: str
    role: str
    division: str
    path: str  # relative path from project root
    emoji: str = ""
    status: str = "active"


# ---------------------------------------------------------------------------
# Top-level company config
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CompanyInfo:
    """Core company identity fields."""

    name: str
    name_cn: str
    tagline: str
    founder: str
    founded: str


class CompanyConfig:
    """Loads and exposes all VWork YAML configuration as typed objects.

    Usage::

        cfg = CompanyConfig()              # auto-detects project root
        cfg = CompanyConfig(Path("/home/dz/vwork"))

        print(cfg.company.name)
        for eid, emp in cfg.employees.items():
            print(emp.name, emp.division)
    """

    def __init__(self, root: Path | None = None) -> None:
        self._root = self._resolve_root(root)
        self._raw_company: dict[str, Any] = {}
        self._raw_divisions: dict[str, Any] = {}
        self._raw_roles: dict[str, Any] = {}
        self._raw_employees: dict[str, Any] = {}

        self._load_all()

        # Parsed objects
        self.company: CompanyInfo = self._parse_company()
        self.runtime: RuntimeConfig = self._parse_runtime()
        self.channels: ChannelsConfig = self._parse_channels()
        self.paths: PathsConfig = self._parse_paths()
        self.divisions: dict[str, DivisionConfig] = self._parse_divisions()
        self.roles: dict[str, RoleConfig] = self._parse_roles()
        self.employees: dict[str, EmployeeConfig] = self._parse_employees()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def root(self) -> Path:
        """Return the resolved project root."""
        return self._root

    def employee(self, employee_id: str) -> EmployeeConfig:
        """Fetch a single employee by ID, raising ``KeyError`` if missing."""
        return self.employees[employee_id]

    def division(self, division_id: str) -> DivisionConfig:
        """Fetch a single division by ID, raising ``KeyError`` if missing."""
        return self.divisions[division_id]

    def role(self, role_id: str) -> RoleConfig:
        """Fetch a single role by ID, raising ``KeyError`` if missing."""
        return self.roles[role_id]

    def employee_workspace(self, employee_id: str) -> Path:
        """Return the absolute workspace path for an employee."""
        emp = self.employee(employee_id)
        return self._root / emp.path

    def division_path(self, division_id: str) -> Path:
        """Return the absolute path for a division."""
        div = self.division(division_id)
        return self._root / div.path

    def employees_in_division(self, division_id: str) -> list[EmployeeConfig]:
        """Return all employees belonging to *division_id*."""
        return [e for e in self.employees.values() if e.division == division_id]

    # ------------------------------------------------------------------
    # Internal: root resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_root(root: Path | None) -> Path:
        if root is not None:
            resolved = root.resolve()
            if not (resolved / "company.yaml").exists():
                raise FileNotFoundError(
                    f"company.yaml not found under {resolved}"
                )
            return resolved
        # Walk upward from this file to find company.yaml
        candidate = Path(__file__).resolve().parent.parent
        if (candidate / "company.yaml").exists():
            return candidate
        raise FileNotFoundError(
            "Cannot locate project root (company.yaml not found). "
            "Pass the root path explicitly."
        )

    # ------------------------------------------------------------------
    # Internal: YAML loading
    # ------------------------------------------------------------------

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise ValueError(f"Expected a YAML mapping in {path}")
        return data

    def _load_all(self) -> None:
        self._raw_company = self._load_yaml(self._root / "company.yaml")
        self._raw_divisions = self._load_yaml(self._root / "org" / "divisions.yaml")
        self._raw_roles = self._load_yaml(self._root / "org" / "roles.yaml")
        self._raw_employees = self._load_yaml(self._root / "org" / "employees.yaml")

    # ------------------------------------------------------------------
    # Internal: parsing helpers
    # ------------------------------------------------------------------

    def _parse_company(self) -> CompanyInfo:
        d = self._raw_company
        return CompanyInfo(
            name=d["name"],
            name_cn=d.get("name_cn", ""),
            tagline=d.get("tagline", ""),
            founder=d.get("founder", ""),
            founded=d.get("founded", ""),
        )

    def _parse_runtime(self) -> RuntimeConfig:
        rt = self._raw_company.get("runtime", {})
        return RuntimeConfig(
            platform=rt.get("platform", "openclaw"),
            default_model=rt.get("default_model", ""),
            premium_model=rt.get("premium_model", ""),
            max_concurrent_agents=int(rt.get("max_concurrent_agents", 4)),
        )

    def _parse_channels(self) -> ChannelsConfig:
        ch = self._raw_company.get("channels", {})
        return ChannelsConfig(
            primary=ch.get("primary", "telegram"),
            internal=ch.get("internal", "filesystem"),
        )

    def _parse_paths(self) -> PathsConfig:
        raw = self._raw_company.get("paths", {})
        # Guarantee every expected key has a sensible default
        defaults = {
            "root": str(self._root),
            "divisions": str(self._root / "divisions"),
            "employees": str(self._root / "employees"),
            "org": str(self._root / "org"),
            "board": str(self._root / "board"),
            "scripts": str(self._root / "scripts"),
            "lib": str(self._root / "lib"),
        }
        merged = {**defaults, **raw}
        return PathsConfig.from_dict(merged)

    def _parse_divisions(self) -> dict[str, DivisionConfig]:
        out: dict[str, DivisionConfig] = {}
        for div_id, div_data in self._raw_divisions.get("divisions", {}).items():
            projects = [
                ProjectRef(
                    id=p["id"],
                    name=p.get("name", p["id"]),
                    type=p.get("type", ""),
                    source=Path(p.get("source", "")),
                )
                for p in div_data.get("projects", []) or []
            ]
            out[div_id] = DivisionConfig(
                id=div_id,
                name=div_data["name"],
                name_cn=div_data.get("name_cn", ""),
                description=div_data.get("description", ""),
                director=div_data.get("director", ""),
                path=div_data.get("path", f"divisions/{div_id}"),
                projects=projects,
            )
        return out

    def _parse_roles(self) -> dict[str, RoleConfig]:
        out: dict[str, RoleConfig] = {}
        for role_id, role_data in self._raw_roles.get("roles", {}).items():
            out[role_id] = RoleConfig(
                id=role_id,
                title=role_data["title"],
                title_cn=role_data.get("title_cn", ""),
                level=role_data.get("level", "mid"),
                permissions=role_data.get("permissions", []),
                responsibilities=role_data.get("responsibilities", []),
                model=role_data.get("model", ""),
            )
        return out

    def _parse_employees(self) -> dict[str, EmployeeConfig]:
        out: dict[str, EmployeeConfig] = {}
        for emp_id, emp_data in self._raw_employees.get("employees", {}).items():
            out[emp_id] = EmployeeConfig(
                id=emp_id,
                name=emp_data["name"],
                name_cn=emp_data.get("name_cn", ""),
                agent_id=emp_data.get("agent_id", ""),
                role=emp_data.get("role", ""),
                division=emp_data.get("division", ""),
                path=emp_data.get("path", ""),
                emoji=emp_data.get("emoji", ""),
                status=emp_data.get("status", "active"),
            )
        return out

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"CompanyConfig(root={self._root!r}, "
            f"employees={len(self.employees)}, "
            f"divisions={len(self.divisions)})"
        )
