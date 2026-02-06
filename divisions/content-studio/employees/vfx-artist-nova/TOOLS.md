# TOOLS.md - VFX Artist Nova's Environment

## ComfyUI
- URL: http://127.0.0.1:8188
- Queue API: http://127.0.0.1:8188/queue
- Output: /home/dz/ComfyUI/output
- Workflows: per-project, check each project's comfyui/ or workflows/ directory

## GPU
- Check status: `nvidia-smi`
- Shared with Fish Audio and other tasks -- coordinate with Sys

## Generation Tools
- **creative-toolkit** (`/home/dz/creative-toolkit`): Shared library for ComfyUI API, LTX2 video gen
- **LTX2 workflows**: i2v (image-to-video), t2v (text-to-video)

## Project Paths
- Fuxi output: `/home/dz/ComfyUI/output/fuxi_*`
- TinyTales output: `/home/dz/ComfyUI/output/tinytales_*`
- Singularity output: `/home/dz/ComfyUI/output/singularity_*`

## Quality Checklist
- Composition matches storyboard spec
- Character consistency across shots
- No artifacts or deformations
- Correct aspect ratio and resolution
- Style consistency within episode
