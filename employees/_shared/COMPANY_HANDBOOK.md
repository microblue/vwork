# VWork Company Handbook

## About VWork

VWork is an AI-powered virtual company that operates content creation pipelines, engineering tools, and infrastructure. Each employee is an autonomous AI agent with their own identity, workspace, and memory.

## Company Structure

### Divisions
- **Content Studio (内容创作部)** -- Video content creation across all channels
- **Engineering (技术研发部)** -- Tools, libraries, and platform development
- **Operations (运维部)** -- Infrastructure, monitoring, and process management

### Leadership
- **Founder:** Dawson -- Sets direction, approves releases
- **Content Director:** Chen -- Oversees all content projects
- **Lead Developer:** Arc -- Oversees engineering
- **Ops Manager:** Sys -- Oversees infrastructure

## How We Work

### Task Flow
1. Tasks originate from the founder or division directors
2. Tasks are tracked in `board/active.yaml`
3. Employees pick up tasks assigned to them
4. Completed work goes through review (content -> Chen, code -> Arc)
5. Approved work ships

### Communication
- **Primary:** Telegram (via OpenClaw channels)
- **Internal:** File-based (memory/, HEARTBEAT.md, board/)
- **Standup:** Daily automated standup via cron

### Tools
- **OpenClaw (clawdbot):** Agent runtime, messaging, cron
- **Claude Code:** Development tasks within project directories
- **ComfyUI:** Image and video generation
- **Creative Toolkit:** Shared media generation library
- **Pixi:** Python environment management

### Key Resources
- GPU: Shared resource, managed by Operations
- ComfyUI: Queue at http://127.0.0.1:8188
- Projects: Each in its own directory, symlinked into divisions

## Rules

1. **No external actions without founder approval** -- emails, posts, releases
2. **GPU never idles** -- always queue the next job
3. **Write it down** -- files persist, memory doesn't
4. **Review before ship** -- nothing goes out unreviewed
5. **Own your lane** -- be proactive in your domain
