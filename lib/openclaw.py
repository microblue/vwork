"""OpenClaw / clawdbot gateway integration for VWork.

Wraps the ``clawdbot`` CLI to register agents, send messages, and manage
cron schedules.  All interaction goes through :func:`subprocess.run`.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import CompanyConfig, EmployeeConfig


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Thin wrapper around a completed subprocess call."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class OpenClawGateway:
    """Interface to the ``clawdbot`` CLI.

    Usage::

        cfg = CompanyConfig()
        gw = OpenClawGateway(cfg)

        # Register an employee as a clawdbot agent
        gw.register_agent("director-chen")

        # Send a message
        gw.send_message("director-chen", "Please review EP002 script.")

        # Add a cron job
        gw.add_cron("director-chen", "0 9 * * *", "Daily standup check.")

        # List all registered agents
        agents = gw.list_agents()
    """

    CLAWDBOT_BIN: str = "clawdbot"

    def __init__(
        self,
        config: CompanyConfig,
        *,
        clawdbot_bin: str | None = None,
        timeout: int = 60,
    ) -> None:
        self._cfg = config
        self._bin = clawdbot_bin or self.CLAWDBOT_BIN
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Agent registration
    # ------------------------------------------------------------------

    def register_agent(
        self,
        employee_id: str,
        *,
        model: str | None = None,
        workspace: Path | None = None,
    ) -> CommandResult:
        """Register an employee as a clawdbot agent.

        Runs::

            clawdbot agents add <agent_id> \\
                --model <model> \\
                --workspace <workspace> \\
                --non-interactive

        If *model* is not provided the role's configured model is used,
        falling back to the company default model.
        """
        emp = self._cfg.employee(employee_id)
        resolved_model = model or self._resolve_model(emp)
        resolved_workspace = workspace or self._cfg.employee_workspace(employee_id)

        cmd = [
            self._bin, "agents", "add",
            emp.agent_id,
            "--model", resolved_model,
            "--workspace", str(resolved_workspace),
            "--non-interactive",
        ]
        return self._run(cmd)

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    def send_message(
        self,
        employee_id: str,
        message: str,
    ) -> CommandResult:
        """Send a message to an employee's agent and deliver it.

        Runs::

            clawdbot agent --agent <agent_id> \\
                --message <message> --deliver
        """
        emp = self._cfg.employee(employee_id)
        cmd = [
            self._bin, "agent",
            "--agent", emp.agent_id,
            "--message", message,
            "--deliver",
        ]
        return self._run(cmd)

    # ------------------------------------------------------------------
    # Cron management
    # ------------------------------------------------------------------

    def add_cron(
        self,
        employee_id: str,
        schedule: str,
        message: str,
        name: str | None = None,
    ) -> CommandResult:
        """Add a cron job that periodically sends *message* to the agent.

        Runs::

            clawdbot cron add \\
                --name <name> \\
                --agent <agent_id> \\
                --cron <cron_expr> \\
                --message <message>
        """
        emp = self._cfg.employee(employee_id)
        job_name = name or f"{emp.agent_id}-cron"
        cmd = [
            self._bin, "cron", "add",
            "--name", job_name,
            "--agent", emp.agent_id,
            "--cron", schedule,
            "--message", message,
        ]
        return self._run(cmd)

    # ------------------------------------------------------------------
    # Listing / querying
    # ------------------------------------------------------------------

    def list_agents(self) -> CommandResult:
        """List all registered clawdbot agents.

        Runs::

            clawdbot agents list
        """
        cmd = [self._bin, "agents", "list"]
        return self._run(cmd)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_model(self, emp: EmployeeConfig) -> str:
        """Pick the best model for *emp* from role config or company default."""
        try:
            role_cfg = self._cfg.role(emp.role)
            if role_cfg.model:
                return role_cfg.model
        except KeyError:
            pass
        return self._cfg.runtime.default_model

    def _run(self, cmd: list[str]) -> CommandResult:
        """Execute a shell command and return a :class:`CommandResult`."""
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
            return CommandResult(
                returncode=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )
        except FileNotFoundError:
            return CommandResult(
                returncode=127,
                stdout="",
                stderr=f"Command not found: {cmd[0]}",
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                returncode=124,
                stdout="",
                stderr=f"Command timed out after {self._timeout}s",
            )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"OpenClawGateway(bin={self._bin!r})"
