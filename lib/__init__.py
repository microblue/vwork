"""VWork -- AI-powered virtual company management library."""

from __future__ import annotations

from .config import CompanyConfig
from .division import DivisionManager
from .employee import EmployeeManager
from .openclaw import OpenClawGateway
from .orchestrator import Orchestrator

__all__ = [
    "CompanyConfig",
    "DivisionManager",
    "EmployeeManager",
    "OpenClawGateway",
    "Orchestrator",
]
