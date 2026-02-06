# VWork - AI Virtual Company

This is the management system for VWork, an AI-powered virtual company where each employee is an autonomous OpenClaw (clawdbot) agent.

## Structure

- `company.yaml` -- Main company configuration
- `org/` -- Organization definitions (divisions, roles, employees)
- `divisions/` -- Division workspaces with projects and employee directories
- `employees/` -- Shared templates and knowledge
- `lib/` -- Python library for company management
- `scripts/` -- CLI tools (hire, status, standup, etc.)
- `skills/` -- OpenClaw skills
- `board/` -- Task board (backlog, active, archive)

## Quick Commands

```bash
# Company status
pixi run status

# Hire a new employee
pixi run hire --name <Name> --id <slug> --role <role> --division <division>

# Register all agents with OpenClaw
pixi run register-agents

# Daily standup
pixi run standup

# Assign a task
pixi run assign --to <employee-id> --task "description"
```

## Agent Pattern

Each employee follows the clawd agent pattern:
- `AGENTS.md` -- Workspace operations manual
- `SOUL.md` -- Personality and values
- `IDENTITY.md` -- Personal identity record
- `ROLE.md` -- Job description and responsibilities
- `TOOLS.md` -- Environment-specific notes
- `memory/` -- Daily logs and persistent memory

## Projects

Projects live in their original directories and are symlinked into divisions:
- `/home/dz/fuxi` -> `divisions/content-studio/projects/fuxi`
- `/home/dz/singularity-channel` -> `divisions/content-studio/projects/singularity`
- `/home/dz/tinytales_channel` -> `divisions/content-studio/projects/tinytales`
- `/home/dz/localmarket` -> `divisions/engineering/projects/localmarket`
- `/home/dz/creative-toolkit` -> `divisions/engineering/projects/creative-toolkit`
