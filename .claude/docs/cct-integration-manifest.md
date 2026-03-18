# CCT Integration Manifest

Source marketplace: `davila7/claude-code-templates`

## Agents installed (prefixed `cct-`)
- cct-devops-engineer
- cct-backend-developer
- cct-fullstack-developer
- cct-test-runner
- cct-security-auditor
- cct-incident-responder
- cct-technical-writer
- cct-workflow-orchestrator

## Commands installed (`~/.claude/commands/cct/`)
- cct-code-review
- cct-debug-error
- cct-refactor-code
- cct-generate-tests
- cct-test-coverage
- cct-security-audit
- cct-security-hardening
- cct-prepare-release
- cct-rollback-deploy
- cct-web-design-reviewer
- cct-create-pr

## Hooks enabled in `settings.json` (PreToolUse/Bash)
- cct-dangerous-command-blocker.py
- cct-prevent-direct-push.py
- cct-conventional-commits.py
- cct-secret-scanner.py

## Skills installed (`~/.claude/skills/`)
- cct-create-plan
- cct-test-driven-development
- cct-systematic-debugging
- cct-frontend-design
- cct-web-design-guidelines
- cct-accessibility-auditor
- cct-context-window-management
