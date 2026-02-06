# VWork - AI 虚拟公司

> 一个由 AI Agent 组成的虚拟公司，每个员工都是独立的 OpenClaw agent，拥有自己的身份、记忆和工作空间。

## 公司概览

| 项目 | 内容 |
|------|------|
| 公司名称 | VWork (虚拟工作室) |
| 创始人 | Dawson |
| 运行平台 | OpenClaw (clawdbot) |
| 默认模型 | claude-sonnet-4-20250514 |
| 高级模型 | claude-opus-4-5-20251101 |

---

## 组织架构

```
VWork
├── 内容创作部 (Content Studio)
│   ├── 🎬 Chen (陈) - 部门主管
│   ├── ✍ Kai - 编剧
│   └── ✨ Nova - 特效师
│
├── 技术研发部 (Engineering)
│   └── ⚡ Arc - 首席开发
│
└── 运维部 (Operations)
    └── 🛠 Sys - 运维经理
```

---

## 员工档案

### 🎬 Chen (陈) - 内容创作部主管

| 属性 | 内容 |
|------|------|
| Agent ID | `vwork-director-chen` |
| 职责 | 统筹内容项目、质量把控、任务分配、审核脚本和成品 |
| 管理项目 | Fuxi (伏羲短剧) |
| 下属 | Kai, Nova |
| 性格 | 细致、有权威感、对质量要求高、用中文沟通内容事务 |

**适合交给 Chen 的任务：**
- 审核脚本质量
- 分配内容制作任务给 Kai 和 Nova
- 检查生成的图片/视频是否符合要求
- 汇报内容部整体进度

---

### ✍ Kai - 编剧

| 属性 | 内容 |
|------|------|
| Agent ID | `vwork-scriptwriter-kai` |
| 职责 | 脚本创作、叙事结构设计、图片生成 Prompt 编写 |
| 汇报给 | Chen |
| 性格 | 有创意、注重叙事、擅长中英文切换 |

**适合交给 Kai 的任务：**
- 写新剧集脚本
- 修改现有脚本
- 为每个镜头编写详细的图片生成 prompt
- 设计故事线和角色发展

---

### ✨ Nova - 特效师

| 属性 | 内容 |
|------|------|
| Agent ID | `vwork-vfx-artist-nova` |
| 职责 | ComfyUI 工作流设计、图片/视频生成、GPU 队列管理、成品合成 |
| 汇报给 | Chen |
| 性格 | 技术流、注重效率、对 GPU 利用率敏感 |

**适合交给 Nova 的任务：**
- 根据脚本生成图片
- 用 LTX2 生成视频
- 检查和优化 ComfyUI 工作流
- 合成最终视频

---

### ⚡ Arc - 首席开发

| 属性 | 内容 |
|------|------|
| Agent ID | `vwork-lead-dev-arc` |
| 职责 | 代码开发、架构设计、代码审查、API 设计 |
| 管理项目 | Creative Toolkit |
| 性格 | 系统性思维、代码洁癖、注重可维护性 |

**适合交给 Arc 的任务：**
- 开发新功能
- 审查代码改动
- 修复 bug
- 设计和维护 creative-toolkit 库

---

### 🛠 Sys - 运维经理

| 属性 | 内容 |
|------|------|
| Agent ID | `vwork-ops-manager-sys` |
| 职责 | GPU 监控、ComfyUI 队列管理、进程守护、服务健康检查 |
| 性格 | 数据驱动、可靠、自动化思维 |

**适合交给 Sys 的任务：**
- 检查 GPU 利用率
- 监控 ComfyUI 队列状态
- 重启挂掉的服务
- 协调 GPU 时间分配（ComfyUI vs Fish Audio）

---

## 项目清单

### 内容创作部项目

| 项目 | 类型 | 路径 | 说明 |
|------|------|------|------|
| Fuxi (伏羲) | 短剧 | `/home/dz/fuxi` | AI 生成短剧系列 |

### 技术研发部项目

| 项目 | 类型 | 路径 | 说明 |
|------|------|------|------|
| Creative Toolkit | 库 | `/home/dz/creative-toolkit` | ComfyUI/LTX2 共享库 |

---

## 使用指南

### 首次设置

```bash
cd /home/dz/vwork

# 1. 安装依赖
pixi install

# 2. 注册所有员工为 OpenClaw agent
pixi run register-agents

# 3. 验证安装
pixi run status
```

### 日常命令

#### 查看公司状态
```bash
pixi run status
```

#### 每日站会
```bash
# 查看所有部门
pixi run standup

# 只看某个部门
pixi run standup --division content-studio

# 发送到 Telegram
pixi run standup --send
```

#### 分配任务
```bash
# 基本用法
pixi run assign --to <员工ID> --task "任务描述"

# 示例
pixi run assign --to director-chen --task "审核 fuxi EP002 脚本"
pixi run assign --to vfx-artist-nova --task "生成 fuxi EP001 S05-S10 镜头"
pixi run assign --to lead-dev-arc --task "修复 creative-toolkit 的视频合成 bug"

# 分配并立即通知员工
pixi run assign --to director-chen --task "紧急审核 EP003" --deliver
```

#### 招聘新员工
```bash
pixi run hire --name <名字> --id <ID> --role <角色> --division <部门>

# 示例：招聘音效师
pixi run hire --name "Echo" --id "sound-designer-echo" \
  --role "vfx-artist" --division "content-studio" --emoji "🎵"

# 可用角色: director, scriptwriter, vfx-artist, lead-developer, ops-manager
# 可用部门: content-studio, engineering, operations
```

### 与员工交互

#### 通过命令行
```bash
# 基本格式
clawdbot agent --agent <agent-id> --message "消息内容"

# 示例
clawdbot agent --agent vwork-director-chen --message "汇报内容部当前状态"
clawdbot agent --agent vwork-vfx-artist-nova --message "检查 ComfyUI 队列"
clawdbot agent --agent vwork-lead-dev-arc --message "审查 creative-toolkit 最新提交"

# 发送并等待回复
clawdbot agent --agent vwork-director-chen --message "你是谁？" --deliver
```

#### 通过 Telegram
配置好 clawdbot Telegram 后，直接在 Telegram 中 @agent 或私聊即可。

### 设置定时任务

```bash
# 每天早上9点站会
clawdbot cron add --name "daily-standup" \
  --agent vwork-director-chen \
  --schedule "0 9 * * *" \
  --message "执行每日站会，汇报所有项目状态并发送到 Telegram" \
  --deliver

# 每5分钟检查 GPU
clawdbot cron add --name "gpu-monitor" \
  --agent vwork-ops-manager-sys \
  --schedule "*/5 * * * *" \
  --message "检查 GPU 利用率，如果空闲且有待办任务则通知相关人员"

# 查看所有定时任务
clawdbot cron list
```

---

## 工作流程

### 内容制作流程

```
1. Dawson 下发需求
   ↓
2. Chen 拆解任务，分配给 Kai 和 Nova
   ↓
3. Kai 编写脚本，包含每个镜头的详细 prompt
   ↓
4. Chen 审核脚本
   ↓
5. Nova 根据脚本生成图片
   ↓
6. Chen 审核图片质量
   ↓
7. Nova 生成视频并合成
   ↓
8. Chen 最终审核
   ↓
9. Dawson 批准发布
```

### 任务分配最佳实践

1. **大任务先给 Chen**：让他拆解并分配给团队
2. **技术问题找 Arc**：代码、API、工具链问题
3. **生成任务找 Nova**：图片、视频、ComfyUI 相关
4. **脚本任务找 Kai**：剧本、文案、prompt 编写
5. **运维问题找 Sys**：GPU、进程、服务状态

---

## 目录结构

```
/home/dz/vwork/
├── company.yaml              # 公司主配置
├── CLAUDE.md                 # Claude Code 项目说明
├── README.md                 # 本文档
├── pixi.toml                 # Python 环境配置
│
├── org/                      # 组织架构定义
│   ├── CHARTER.md           # 公司使命、价值观
│   ├── divisions.yaml       # 事业部注册表
│   ├── roles.yaml           # 角色模板
│   └── employees.yaml       # 员工注册表
│
├── divisions/                # 事业部目录
│   ├── content-studio/      # 内容创作部
│   │   ├── DIVISION.md     # 部门章程
│   │   ├── HEARTBEAT.md    # 任务清单
│   │   ├── projects/       # 项目 symlink
│   │   └── employees/      # 员工工作空间
│   ├── engineering/         # 技术研发部
│   └── operations/          # 运维部
│
├── employees/                # 共享员工资源
│   ├── _template/           # 新员工模板
│   └── _shared/             # 公司手册
│
├── lib/                      # Python 库
├── scripts/                  # CLI 工具
├── skills/                   # OpenClaw 技能
└── board/                    # 任务看板
    ├── active.yaml          # 当前任务
    ├── backlog.yaml         # 待办任务
    └── archive/             # 已完成任务
```

---

## 常见问题

### Q: 员工没有响应？
检查是否已注册 agent：
```bash
clawdbot agents list
```
如果没有，运行 `pixi run register-agents`

### Q: 如何查看员工的记忆？
每个员工的记忆在其 `memory/` 目录：
```bash
ls /home/dz/vwork/divisions/content-studio/employees/director-chen/memory/
```

### Q: 如何修改员工性格？
编辑员工的 `SOUL.md` 文件：
```bash
vim /home/dz/vwork/divisions/content-studio/employees/director-chen/SOUL.md
```

### Q: 如何添加新的角色类型？
编辑 `org/roles.yaml` 添加新角色定义。

### Q: GPU 被占用怎么办？
让 Sys 协调：
```bash
clawdbot agent --agent vwork-ops-manager-sys \
  --message "ComfyUI 和 Fish Audio 需要共享 GPU，请协调调度"
```

---

## 快速参考卡

| 操作 | 命令 |
|------|------|
| 查看状态 | `pixi run status` |
| 每日站会 | `pixi run standup` |
| 分配任务 | `pixi run assign --to <ID> --task "..."` |
| 招聘员工 | `pixi run hire --name X --id X --role X --division X` |
| 注册 Agent | `pixi run register-agents` |
| 与员工对话 | `clawdbot agent --agent <ID> --message "..."` |
| 添加定时任务 | `clawdbot cron add --name X --agent X --schedule "..." --message "..."` |

---

*VWork - 让 AI 像团队一样协作*
