# TOOLS.md - Ops Manager Sys's Environment

## GPU Monitoring
- Status: `nvidia-smi`
- Detailed: `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv`

## ComfyUI
- URL: http://127.0.0.1:8188
- Queue: `curl -s http://127.0.0.1:8188/queue`
- Output: /home/dz/ComfyUI/output

## Process Management
- Check running: `ps aux | grep -E 'comfyui|fish_audio'`
- ComfyUI dir: /home/dz/ComfyUI

## Cron (via clawdbot)
- List: `clawdbot cron list`
- Add: `clawdbot cron add --name <name> --schedule <cron> --agent <id> --message <msg>`

## Key Directories
- ComfyUI: /home/dz/ComfyUI
- VWork: /home/dz/vwork
- All project paths: see company.yaml
