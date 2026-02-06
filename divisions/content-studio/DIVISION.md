# Content Studio (内容创作部)

## Mission

Produce high-quality AI-generated video content across multiple channels, from script to final render.

## Director

**Chen (陈)** -- Oversees all content projects, manages the creative pipeline, ensures quality.

## Team

| Employee | Role | Focus |
|----------|------|-------|
| Chen | Director | Project management, quality control, task assignment |
| Kai | Scriptwriter | Scripts, narrative structure, prompt engineering |
| Nova | VFX Artist | ComfyUI workflows, image/video generation |

## Projects

### Fuxi (伏羲) -- Short Drama
- Path: `projects/fuxi`
- Format: AI-generated short drama episodes
- Pipeline: Script -> Storyboard -> Image Gen -> Video Gen -> Voice -> Composite

### Singularity Channel -- Finance News
- Path: `projects/singularity`
- Format: Daily AI-powered finance news commentary
- Pipeline: News Scrape -> Analysis -> Script -> Generation -> Upload

### TinyTales -- Children's Animation
- Path: `projects/tinytales`
- Format: Short animated stories for children
- Pipeline: Story -> Illustration -> Animation -> Voice -> Composite

## Workflow

1. **Kai** writes/updates scripts
2. **Chen** reviews and approves scripts
3. **Nova** generates visual assets via ComfyUI
4. **Chen** reviews quality of generated assets
5. **Nova** composites final video
6. **Chen** final review and approval for release

## Quality Gates

- All scripts reviewed by Chen before generation
- All generated images reviewed against storyboard requirements
- Final video approved by Chen before publishing
- Voice-over quality checked against character profiles
