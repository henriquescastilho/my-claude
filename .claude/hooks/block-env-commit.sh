#!/bin/bash
# Block git add/commit of .env files and credential files
# Reads JSON from stdin (PreToolUse hook)

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block git add of dangerous files
if echo "$COMMAND" | grep -qE 'git\s+add.*\.(env|env\.|credentials|key|pem|p12|pfx)'; then
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"BLOQUEADO: Tentativa de adicionar arquivo com credenciais ao git. Use .gitignore para excluir .env e similares."}}'
  exit 0
fi

# Block git add -A or git add . when .env exists in the directory
if echo "$COMMAND" | grep -qE 'git\s+add\s+(-A|\.)'; then
  CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
  if [ -n "$CWD" ] && ls "$CWD"/.env* 2>/dev/null | head -1 > /dev/null 2>&1; then
    # Check if .gitignore exists and covers .env
    if [ -f "$CWD/.gitignore" ] && grep -q '\.env' "$CWD/.gitignore" 2>/dev/null; then
      exit 0  # .gitignore already covers it
    else
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"BLOQUEADO: git add -A/. detectou .env no diretório sem .gitignore cobrindo. Adicione .env ao .gitignore primeiro."}}'
      exit 0
    fi
  fi
fi

exit 0
