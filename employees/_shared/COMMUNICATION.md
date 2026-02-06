# Communication Protocol

## Between Employees

Employees coordinate through files, not real-time chat.

### Task Requests
To request work from another employee:
1. Add a task to `board/active.yaml` with the target employee
2. The employee will see it on their next heartbeat/session
3. Results will be written to the task or relevant project files

### Status Updates
- Each division maintains a `HEARTBEAT.md` with current status
- Daily standups aggregate across divisions
- Check `board/active.yaml` for company-wide task status

### Escalation
If blocked:
1. Document the blocker in your daily memory file
2. Add a note to the division's HEARTBEAT.md
3. If urgent, the system will notify the founder via Telegram

## With Founder (Dawson)

- Telegram is the primary channel
- Status reports: automated via standup cron
- Urgent issues: direct message
- Approvals: tag in task board, wait for response

## Conventions

- Use employee names in task assignments (Chen, Kai, Nova, Arc, Sys)
- Reference projects by ID (fuxi, singularity, tinytales, localmarket, creative-toolkit)
- Dates in ISO format (YYYY-MM-DD)
- All content in Chinese unless the context is English-only code
