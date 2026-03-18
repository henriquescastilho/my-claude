# my-claude

Public, sanitized export of a large local Claude setup.

This repository does not mirror `~/.claude` blindly. It keeps the reusable parts:

- `.claude/agents`
- `.claude/commands`
- `.claude/hooks`
- `.claude/skills`
- `.claude/get-shit-done`
- `.claude/docs`
- `.claude/dashboard`
- `.claude/tools`
- `.claude/profiles`
- `.claude/settings.json`
- `.claude/plugins/*.json` manifests
- `.claude-mem-hybrid` runtime code and compose files
- `.claude-mem/settings.template.json`

It intentionally excludes private or high-churn state:

- auth, sessions, telemetry, debug, file history, shell snapshots
- task/todo runtime stores
- agent memory and per-project memory
- plugin caches and vendored marketplace trees
- database files, Redis/Postgres data, logs

## Structure

- `.claude/`: main Claude configuration, prompts, hooks, workflows, and manifests
- `.claude-mem-hybrid/`: MCP memory server backed by PostgreSQL + Redis
- `.claude-mem/`: template settings for the older local memory stack
- `docs/`: architecture notes and generated inventories
- `scripts/`: install and inventory tooling

## Install

1. Clone this repo.
2. Review `.claude/settings.json`, `.claude/profiles/*.json`, and `.claude/settings.local.template.json`.
3. Run:

```bash
./scripts/install.sh
```

4. If you use the hybrid memory server, start it with:

```bash
cd ~/.claude-mem-hybrid
docker compose up -d
```

5. Rebuild inventories after local changes:

```bash
python3 scripts/build_inventory.py
```

## Plugins

The repo publishes plugin manifests, not plugin caches. That keeps the repo small and auditable while preserving:

- installed plugin names
- pinned marketplace names
- pinned plugin versions and commit SHAs
- enabled plugin matrices in global settings and profiles

## Notes

- Path references were rewritten to use `$HOME` or `~`.
- `settings.local.template.json` is a template. Keep machine-specific permissions local.
- The legacy `.claude-mem` data stores are intentionally excluded; only configuration shape is kept.
