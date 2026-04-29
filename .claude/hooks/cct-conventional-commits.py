#!/usr/bin/env python3
import json
import sys
import re

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only validate git commit commands
if tool_name != "Bash" or "git commit" not in command:
    sys.exit(0)

# Extract commit message from -m flag
# Try heredoc format first: -m "$(cat <<'EOF' ... EOF)"
heredoc_match = re.search(r'-m\s+"?\$\(cat\s+<<[\s]*["\']?EOF["\']?\s*\n(.+?)\n\s*EOF', command, re.DOTALL)
if heredoc_match:
    commit_msg = heredoc_match.group(1).strip()
else:
    # Handle both -m "message" and -m 'message' formats
    match = re.search(r'git commit.*?-m\s+["\']([^"\']+)["\']', command)
    if match:
        commit_msg = match.group(1)
    else:
        sys.exit(0)  # Can't extract message, allow it

# Check if message follows Conventional Commits format
# Format: type(scope)?: description
# Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
conventional_pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?:\s.+'

# Validate only the first line (subject) of the commit message
first_line = commit_msg.split('\n')[0].strip()
if not re.match(conventional_pattern, first_line):
    reason = f"""❌ Invalid commit message format

Your message: {first_line}

Commit messages must follow Conventional Commits:
  type(scope): description

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation changes
  style:    Code style changes (formatting)
  refactor: Code refactoring
  perf:     Performance improvements
  test:     Adding or updating tests
  chore:    Maintenance tasks
  ci:       CI/CD changes
  build:    Build system changes
  revert:   Revert previous commit

Examples:
  ✅ feat: add user authentication
  ✅ feat(auth): implement JWT tokens
  ✅ fix: resolve memory leak in parser
  ✅ fix(api): handle null responses
  ✅ docs: update API documentation

Invalid:
  ❌ Added new feature (no type)
  ❌ feat:add feature (missing space after colon)
  ❌ feature: add login (wrong type, use 'feat')

💡 Tip: Start your message with one of the types above followed by a colon and space."""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Allow the command
sys.exit(0)
