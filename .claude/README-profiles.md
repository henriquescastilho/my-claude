# Claude Profiles Wrapper

This machine maps custom mode flags in `~/.zshrc`:

- `claude --xquads ...`
  - Injects `--settings ~/.claude/profiles/xquads.json`
  - Adds `--add-dir ~/xquads-squads` when that directory exists
- `claude --team ...`
  - Injects `--settings ~/.claude/profiles/team.json`
  - Defaults to `--agent pro-workflow:orchestrator` if no `--agent` is provided
- `claude --yolo ...`
  - Injects `--settings ~/.claude/profiles/yolo.json`
  - Injects `--dangerously-skip-permissions`
  - Requires `CLAUDE_ALLOW_YOLO=1`

## Profile files

- `~/.claude/profiles/xquads.json`
- `~/.claude/profiles/team.json`
- `~/.claude/profiles/yolo.json`

## Safety constraints

- Only one of `--xquads`, `--team`, `--yolo` is allowed per command.
- Mode flags cannot be combined with manual `--settings`.

## Quick rollback

1. Restore backup:
   - `cp ~/.zshrc.bak-20260310-1511 ~/.zshrc`
2. Reload shell:
   - `source ~/.zshrc`
3. Optional cleanup:
   - `rm -rf ~/.claude/profiles`
   - `rm ~/.claude/README-profiles.md`
