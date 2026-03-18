#!/usr/bin/env bash
set -euo pipefail

BASE="${HOME}/.claude"

mkd() {
  mkdir -p "$1"
}

mkf() {
  local file="$1"
  local content="$2"
  if [ ! -e "$file" ]; then
    printf "%s\n" "$content" > "$file"
  fi
}

mkx() {
  local file="$1"
  local content="$2"
  if [ ! -e "$file" ]; then
    printf "%s\n" "$content" > "$file"
    chmod +x "$file"
  fi
}

# Core directories from reel
for d in \
  commands/gsd \
  commands/memory \
  commands/security \
  commands/taskmaster \
  commands/utility-cmds \
  commands/workflow \
  dashboard \
  docs/hooks \
  docs/file-history \
  docs/file-persist \
  docs/frameworks \
  docs/get-shit-done/bin \
  docs/get-shit-done/references \
  docs/get-shit-done/templates \
  docs/get-shit-done/workflows \
  hooks \
  learning/episodes \
  learning/errors \
  learning/logs \
  learning/metrics \
  learning/patterns \
  memory/episodic \
  memory/semantic \
  memory/vectordb \
  memory/working \
  output-styles \
  plugins/cache \
  plugins/marketplaces/claude-code-plugins \
  plugins/marketplaces/claude-plugins-official/plugins \
  plugins/marketplaces/oliver-kriska

do
  mkd "$BASE/$d"
done

# Commands placeholders
for f in next new plan update verify; do
  mkf "$BASE/commands/gsd/${f}.md" "# ${f}\n\nPlaceholder command for gsd/${f}."
done

for f in mem-context mem-delete mem-export mem-list mem-recall mem-save mem-search mem-stats; do
  mkf "$BASE/commands/memory/${f}.md" "# ${f}\n\nPlaceholder command for memory/${f}."
done

mkf "$BASE/commands/security/harden.md" "# harden\n\nSecurity hardening checklist placeholder."
mkf "$BASE/commands/security/secret-scan.md" "# secret-scan\n\nSecret scanning workflow placeholder."
mkf "$BASE/commands/security/security-scan.md" "# security-scan\n\nSecurity scanning workflow placeholder."

for f in add-task update-task tm-list tm-next tm-progress tm-search to-done to-in-progress; do
  mkf "$BASE/commands/taskmaster/${f}.md" "# ${f}\n\nTaskmaster command placeholder for ${f}."
done

for f in agents analytics analyze-project debug doctor; do
  mkf "$BASE/commands/utility-cmds/${f}.md" "# ${f}\n\nUtility command placeholder for ${f}."
done

mkx "$BASE/commands/workflow/batch.sh" "#!/usr/bin/env bash\nset -euo pipefail\necho '[workflow/batch] placeholder'"
mkx "$BASE/commands/workflow/dashboard.sh" "#!/usr/bin/env bash\nset -euo pipefail\necho '[workflow/dashboard] placeholder'"
for f in analytics smart-workflow test van verify vibe-code; do
  mkf "$BASE/commands/workflow/${f}.md" "# ${f}\n\nWorkflow command placeholder for ${f}."
done

# Dashboard placeholders
mkf "$BASE/dashboard/README.md" "# OSA Dashboard\n\nBootstrap placeholder for dashboard tools."
for f in osa-dashboard.html QUICKSTART.md QUICK-START-MONITOR.md STATUS_DASHBOARD_SUMMARY.md; do
  mkf "$BASE/dashboard/${f}" "# ${f}\n\nPlaceholder."
done

mkx "$BASE/dashboard/osa-status.sh" "#!/usr/bin/env bash\nset -euo pipefail\necho '{\"status\":\"ok\",\"source\":\"osa-status.sh\"}'"
mkx "$BASE/dashboard/osa-status-fast.sh" "#!/usr/bin/env bash\nset -euo pipefail\necho '{\"status\":\"ok\",\"source\":\"osa-status-fast.sh\"}'"
mkx "$BASE/dashboard/status.sh" "#!/usr/bin/env bash\nset -euo pipefail\n\"${HOME}/.claude/dashboard/osa-status.sh\""
mkx "$BASE/dashboard/test-monitor.sh" "#!/usr/bin/env bash\nset -euo pipefail\n\"${HOME}/.claude/dashboard/osa-status-fast.sh\""
mkf "$BASE/dashboard/osa-dashboard.py" "#!/usr/bin/env python3\nprint('dashboard placeholder')"
mkf "$BASE/dashboard/osa-monitor.py" "#!/usr/bin/env python3\nprint('monitor placeholder')"

# Docs placeholders
mkf "$BASE/docs/hooks/README.md" "# Hooks Docs\n\nIndex of hook architecture and integration docs."
for f in ARCHITECTURE.md INTEGRATION-GUIDE.md MCP-CACHE-README.md OPTIMIZATION-GUIDE.md agents.md commands.md; do
  mkf "$BASE/docs/hooks/${f}" "# ${f}\n\nPlaceholder documentation."
done
mkf "$BASE/docs/frameworks/orchestrator.py" "#!/usr/bin/env python3\nprint('orchestrator placeholder')"
mkf "$BASE/docs/frameworks/pact_framework.py" "#!/usr/bin/env python3\nprint('pact framework placeholder')"
mkf "$BASE/docs/frameworks/swarm_executor.py" "#!/usr/bin/env python3\nprint('swarm executor placeholder')"
mkf "$BASE/docs/get-shit-done/bin/gsd-tools.cjs" "#!/usr/bin/env node\nconsole.log('gsd tools placeholder');"
mkf "$BASE/docs/get-shit-done/bin/gsd-tools.test.cjs" "#!/usr/bin/env node\nconsole.log('gsd tools test placeholder');"
for f in roadmap state summary-complex summary-minimal summary-standard summary UAT user-setup verification-report; do
  mkf "$BASE/docs/get-shit-done/templates/${f}.md" "# ${f}\n\nTemplate placeholder."
done
for f in add-phase audit-milestone check-todos cleanup complete-milestone discovery-phase discuss-phase execute-phase execute-plan health help new-milestone new-project; do
  mkf "$BASE/docs/get-shit-done/workflows/${f}.md" "# ${f}\n\nWorkflow placeholder."
done
mkf "$BASE/docs/get-shit-done/references/README.md" "# References\n\nPlace reference documents here."

# Hooks executable placeholders
for f in pre-compact.sh security-check.sh session-end-cleanup.sh session-start.sh setup-init.sh smart-dispatcher.sh stop-verify.sh task-completed.sh teammate-idle.sh update-scratchpad.sh; do
  mkx "$BASE/hooks/${f}" "#!/usr/bin/env bash\nset -euo pipefail\necho '[hook:${f}] placeholder'"
done
for f in smart-permission.py smart-stop-gate.py subagent-start.py subagent-stop.py unified-post-hook.py validate-prompt.py validate-structure.py; do
  mkx "$BASE/hooks/${f}" "#!/usr/bin/env python3\nprint('[hook:${f}] placeholder')"
done

# Learning & memory files
mkf "$BASE/learning/sessions.log" ""
mkf "$BASE/learning/events.db" ""
mkf "$BASE/memory/vectordb/ids.json" "[]"
mkf "$BASE/memory/vectordb/metadata.json" "{}"
mkf "$BASE/memory/README.md" "# Memory System\n\nPersistent memory structure scaffold."

# Output styles
mkf "$BASE/output-styles/engineering.md" "# Engineering Style\n\nConcise, evidence-first, implementation-focused output style."
mkf "$BASE/output-styles/mentor.md" "# Mentor Style\n\nDidactic but pragmatic output style."

# Marketplace scaffolding
mkd "$BASE/plugins/marketplaces/claude-code-plugins/.claude/commands"
mkf "$BASE/plugins/marketplaces/claude-code-plugins/.claude/commands/commit-push-pr.md" "# commit-push-pr\n\nPlugin command placeholder."
mkf "$BASE/plugins/marketplaces/claude-code-plugins/.claude/commands/dedupe.md" "# dedupe\n\nPlugin command placeholder."
mkf "$BASE/plugins/marketplaces/claude-code-plugins/.claude/commands/oncall-triage.md" "# oncall-triage\n\nPlugin command placeholder."
mkf "$BASE/plugins/marketplaces/claude-code-plugins/.claude-plugin" "name: claude-code-plugins\nversion: 0.0.1"
mkd "$BASE/plugins/marketplaces/claude-plugins-official/plugins/skill-creator"
mkf "$BASE/plugins/marketplaces/claude-plugins-official/plugins/README.md" "# Official Plugins\n\nPlace official plugin copies here."
mkd "$BASE/plugins/marketplaces/oliver-kriska/.claude/agents"
mkd "$BASE/plugins/marketplaces/oliver-kriska/.claude/commands"
mkf "$BASE/plugins/marketplaces/oliver-kriska/.claude/agents/docs-validation-orchestrator.md" "# docs-validation-orchestrator\n\nPlaceholder agent."
mkf "$BASE/plugins/marketplaces/oliver-kriska/.claude/agents/phoenix-project-analyzer.md" "# phoenix-project-analyzer\n\nPlaceholder agent."
mkf "$BASE/plugins/marketplaces/oliver-kriska/.claude/commands/psql-query.md" "# psql-query\n\nPlaceholder command."
mkf "$BASE/plugins/marketplaces/oliver-kriska/.claude/commands/techdebt.md" "# techdebt\n\nPlaceholder command."

# Root docs
mkf "$BASE/README-REEL-STRUCTURE.md" "# .claude Reel Structure\n\nThis scaffold was generated by bootstrap-reel-structure.sh and is safe to re-run.\nIt creates missing directories/files without overwriting existing content."

printf "Bootstrap complete at %s\n" "$BASE"
