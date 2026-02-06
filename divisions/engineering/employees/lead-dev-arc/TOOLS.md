# TOOLS.md - Lead Developer Arc's Environment

## Project Paths
- LocalMarket: `/home/dz/localmarket`
- Creative Toolkit: `/home/dz/creative-toolkit`

## Development Tools
- Python 3.12+ with pixi for environment management
- ruff for formatting and linting
- pytest for testing
- git for version control

## Key APIs
- ComfyUI: http://127.0.0.1:8188 (creative-toolkit wraps this)
- LTX2: via creative-toolkit workflows

## Build & Test
- `pixi run test` in each project
- `pixi run lint` for code style
- Check project-specific pixi.toml for available tasks
