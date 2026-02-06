# Operations (运维部)

## Mission

Keep the infrastructure running. Monitor GPU utilization, manage processes, and ensure all services stay healthy.

## Director

**Sys** -- Operations manager responsible for infrastructure, monitoring, and process management.

## Team

| Employee | Role | Focus |
|----------|------|-------|
| Sys | Ops Manager | GPU monitoring, process management, service health |

## Responsibilities

- Monitor GPU utilization and ComfyUI queue
- Manage service lifecycle (ComfyUI, Fish Audio, etc.)
- Handle GPU time-sharing between services
- Maintain cron jobs and heartbeat schedules
- System health alerts

## Key Systems

- **GPU:** NVIDIA GPU shared across ComfyUI, Fish Audio, and other tasks
- **ComfyUI:** http://127.0.0.1:8188 -- primary rendering engine
- **Process Management:** Service start/stop/restart
- **Cron:** Scheduled tasks via clawdbot cron

## SLA

- GPU idle time < 5 minutes when there are pending tasks
- ComfyUI availability > 99% during work hours
- Alert on service failure within 1 heartbeat cycle
