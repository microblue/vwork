# VWork Manager Skill

## Summary
Manage the VWork virtual company -- check status, assign tasks, run standups, hire employees.

## Commands

### Company Status
Check the overall company status including all divisions, employees, and active tasks.
```
Check company status: pixi run status (in /home/dz/vwork)
```

### Hire Employee
Create a new employee with a workspace and register them as an OpenClaw agent.
```
pixi run hire --name <Name> --id <slug> --role <role> --division <division>
```

Available roles: director, scriptwriter, vfx-artist, lead-developer, ops-manager
Available divisions: content-studio, engineering, operations

### Register Agents
Register all employees as OpenClaw agents (or re-register a specific one).
```
pixi run register-agents
pixi run register-agents --employee <id>
```

### Daily Standup
Generate a standup report across all divisions.
```
pixi run standup
pixi run standup --division content-studio
pixi run standup --send  # send via Telegram
```

### Assign Task
Create and assign a task to an employee.
```
pixi run assign --to <employee-id> --task "description"
pixi run assign --to director-chen --task "Review fuxi EP002 script" --deliver
```

## File Locations
- Company config: `/home/dz/vwork/company.yaml`
- Org structure: `/home/dz/vwork/org/`
- Divisions: `/home/dz/vwork/divisions/`
- Task board: `/home/dz/vwork/board/`
- Scripts: `/home/dz/vwork/scripts/`

## Employee Quick Reference
| ID | Name | Division | Role |
|----|------|----------|------|
| director-chen | Chen | content-studio | Director |
| scriptwriter-kai | Kai | content-studio | Scriptwriter |
| vfx-artist-nova | Nova | content-studio | VFX Artist |
| lead-dev-arc | Arc | engineering | Lead Developer |
| ops-manager-sys | Sys | operations | Ops Manager |
