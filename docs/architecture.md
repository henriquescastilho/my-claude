# Architecture

## Main Layers

### 1. Claude Core

The exported `.claude` tree is organized around six main subsystems:

- `agents/`: specialist prompts with frontmatter metadata such as `name`, `description`, `model`, and sometimes `memory`
- `commands/`: slash-command style workflows grouped into `cct`, `gsd`, `memory`, `security`, `taskmaster`, `utility-cmds`, and `workflow`
- `hooks/`: enforcement and automation hooks for bash safety, direct-push prevention, secret scanning, context monitoring, and status line updates
- `skills/`: reusable local skill folders with `SKILL.md`
- `get-shit-done/`: the largest internal orchestration subsystem, with CLI helpers, workflow prompts, templates, and references
- `plugins/`: only manifest-level metadata is published here

Archived prompt collections are also preserved in:

- `agents-archive/`
- `agents-backups/`

### 2. Profiles And Settings

The exported settings model has:

- one global `.claude/settings.json`
- one machine-local template `.claude/settings.local.template.json`
- multiple profile files under `.claude/profiles/`

Global settings define:

- model default
- enabled plugins
- extra marketplaces
- shell hook wiring
- status line integration

Profiles define:

- mode name through `CLAUDE_PROFILE_MODE`
- model selection
- plugin activation matrix by persona or workflow

### 3. GSD Workflow System

`.claude/get-shit-done` is a standalone planning and execution framework embedded into the Claude setup. It contains:

- `bin/gsd-tools.cjs`: workflow helper CLI
- `workflows/`: operational playbooks such as planning, executing, validating, and transitioning phases
- `templates/`: markdown and JSON templates used by the workflows
- `references/`: normative guidance for Git, TDD, checkpoints, model profiles, and planning state

Most `gsd` commands and several `gsd-*` agents depend on this subtree.

### 4. Hybrid Memory

`.claude-mem-hybrid` provides the active MCP memory implementation:

- `mcp_memory_server.py`: stdio MCP server
- `docker-compose.yml`: PostgreSQL + Redis local stack
- `init.sql`: primary schema
- `run_mem_hybrid.sh`: convenience launcher

### 5. Legacy Memory

`.claude-mem/settings.template.json` preserves the configuration shape of the older local memory system without publishing any live state or embeddings.

### 6. Codex Layer

The exported `.codex` tree mirrors the reusable local Codex setup:

- `AGENTS.md`: user instruction baseline
- `agents/`: Codex specialist prompts
- `skills/`: local and system skill directories
- `vendor_imports/skills/`: curated upstream skills tree
- `vendor_imports/claude/marketplaces/`: vendored Claude plugin marketplace trees
- `config.template.toml`: sanitized config template

The install script also syncs `.codex/vendor_imports/claude/marketplaces` into `~/.claude/plugins/marketplaces` so the Claude side has plugin source trees available without duplicating them in the repository.

Vendored upstream trees are intentionally preserved close to upstream source. That means they may include example absolute paths, `.env.example` files, placeholder keys, demos, or benchmark artifacts that are not part of the local machine state.

### 7. Generated Inventories

`docs/inventory/` is generated from the exported repo so the published setup stays inspectable without depending on private local state.

## Publication Model

### Published directly

- prompts
- skills
- hooks
- workflows
- templates
- dashboards
- tool scripts
- settings and profile templates
- plugin manifests
- memory server code

### Published only as templates or sanitized manifests

- `.claude/settings.local.template.json`
- `.claude-mem/settings.template.json`
- plugin install locations and cache paths rewritten to `$HOME`

### Excluded

- auth
- per-project state
- session history
- telemetry
- backups
- caches
- plugin marketplaces
- plugin unpacked caches
- DB files, vector stores, Redis append-only files, logs
