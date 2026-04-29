#!/usr/bin/env bash

input=$(cat)
json=$(printf '%s' "$input" | tr '\r\n' ' ')

extract_string_after_marker() {
  local marker="$1"
  local key="$2"
  local section="$json"

  case "$section" in
    *\"$marker\"*) section=${section#*\""$marker"\"} ;;
    *) return 0 ;;
  esac

  case "$section" in
    *\"$key\"*) section=${section#*\""$key"\"} ;;
    *) return 0 ;;
  esac

  section=${section#*:}
  printf '%s' "$section" | sed -nE 's/^[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p' | head -n1
}

extract_number_after_marker() {
  local marker="$1"
  local key="$2"
  local section="$json"

  case "$section" in
    *\"$marker\"*) section=${section#*\""$marker"\"} ;;
    *) return 0 ;;
  esac

  case "$section" in
    *\"$key\"*) section=${section#*\""$key"\"} ;;
    *) return 0 ;;
  esac

  section=${section#*:}
  printf '%s' "$section" | sed -nE 's/^[^0-9-]*(-?[0-9]+([.][0-9]+)?).*/\1/p' | head -n1
}

round_percent() {
  local value="$1"
  [ -n "$value" ] || return 1
  printf '%.0f' "$value" 2>/dev/null
}

build_bar() {
  local percentage="$1"
  local filled="$2"
  local bar=""
  local i=1

  while [ "$i" -le 10 ]; do
    if [ "$i" -le "$filled" ]; then
      bar="${bar}█"
    else
      bar="${bar}░"
    fi
    i=$((i + 1))
  done

  printf '[%s] %s%%' "$bar" "$percentage"
}

format_limit() {
  local raw="$1"
  local rounded=""

  if rounded=$(round_percent "$raw"); then
    printf '%s%%' "$rounded"
  else
    printf -- '--'
  fi
}

model=$(extract_string_after_marker "model" "display_name")
[ -n "$model" ] || model="Claude Code"
model=$(printf '%s' "$model" | sed 's/\\"/"/g')

current_dir=$(extract_string_after_marker "workspace" "current_dir")
[ -n "$current_dir" ] || current_dir=$(pwd)
normalized_dir=$(printf '%s' "$current_dir" | sed 's|\\\\|/|g; s|\\|/|g; s|\\/|/|g' | awk '{ gsub(/\/+/, "/"); print }')

relative_dir=$(printf '%s' "$normalized_dir" | sed -nE 's|.*/[Uu]sers/[^/]*/||p')
[ -n "$relative_dir" ] || relative_dir=$(printf '%s' "$normalized_dir" | sed -nE 's|.*/[Hh]ome/[^/]*/||p')
[ -n "$relative_dir" ] || relative_dir=${normalized_dir##*/}
[ -n "$relative_dir" ] || relative_dir="-"

branch="-"
if command -v git >/dev/null 2>&1; then
  maybe_branch=$(GIT_OPTIONAL_LOCKS=0 git -C "$normalized_dir" branch --show-current 2>/dev/null || true)
  if [ -z "$maybe_branch" ]; then
    maybe_branch=$(GIT_OPTIONAL_LOCKS=0 git -C "$normalized_dir" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
  fi
  if [ -n "$maybe_branch" ] && [ "$maybe_branch" != "HEAD" ]; then
    branch="$maybe_branch"
  fi
fi

context_raw=$(extract_number_after_marker "context_window" "used_percentage")
if context_pct=$(round_percent "$context_raw"); then
  :
else
  context_pct=0
fi

if [ "$context_pct" -lt 0 ]; then
  context_pct=0
elif [ "$context_pct" -gt 100 ]; then
  context_pct=100
fi

filled_blocks=$(awk "BEGIN { value=$context_pct; print int((value + 5) / 10) }")
if [ "$filled_blocks" -gt 10 ]; then
  filled_blocks=10
fi

RESET=$'\033[0m'
DIM=$'\033[90m'
GREEN=$'\033[32m'
YELLOW=$'\033[33m'
RED=$'\033[31m'

if [ "$context_pct" -le 60 ]; then
  context_color="$GREEN"
elif [ "$context_pct" -le 80 ]; then
  context_color="$YELLOW"
else
  context_color="$RED"
fi

context_segment=$(build_bar "$context_pct" "$filled_blocks")
five_hour=$(format_limit "$(extract_number_after_marker "five_hour" "used_percentage")")
seven_day=$(format_limit "$(extract_number_after_marker "seven_day" "used_percentage")")

# 5-hour countdown: compute remaining time from resets_at epoch
five_hour_resets=$(extract_number_after_marker "five_hour" "resets_at")
five_hour_suffix=""
if [ -n "$five_hour_resets" ] && [ "$five_hour_resets" -gt 0 ] 2>/dev/null; then
  now=$(date +%s)
  diff=$(( five_hour_resets - now ))
  if [ "$diff" -gt 0 ]; then
    hours=$(( diff / 3600 ))
    mins=$(( (diff % 3600) / 60 ))
    if [ "$hours" -gt 0 ]; then
      five_hour_suffix=" (${hours}h${mins}m left)"
    else
      five_hour_suffix=" (${mins}m left)"
    fi
  else
    five_hour_suffix=" (resetting)"
  fi
fi

# 7-day reset date: format resets_at epoch as "Apr 21"
seven_day_resets=$(extract_number_after_marker "seven_day" "resets_at")
seven_day_suffix=""
if [ -n "$seven_day_resets" ] && [ "$seven_day_resets" -gt 0 ] 2>/dev/null; then
  seven_day_suffix=" (resets $(date -r "$seven_day_resets" "+%b %-d" 2>/dev/null || date -d "@$seven_day_resets" "+%b %-d" 2>/dev/null))"
fi

separator=" ${DIM}|${RESET} "

# Total session tokens (real values from JSON)
format_tokens() {
  local val="$1"
  if [ -z "$val" ] || [ "$val" = "0" ]; then
    printf '0'
    return
  fi
  if [ "$val" -ge 1000000 ] 2>/dev/null; then
    printf '%s' "$(awk "BEGIN { printf \"%.1f\", $val / 1000000 }")M"
  elif [ "$val" -ge 1000 ] 2>/dev/null; then
    printf '%s' "$(awk "BEGIN { printf \"%.0f\", $val / 1000 }")K"
  else
    printf '%s' "$val"
  fi
}

total_in=$(extract_number_after_marker "context_window" "total_input_tokens")
total_out=$(extract_number_after_marker "context_window" "total_output_tokens")
cost_usd=$(extract_number_after_marker "cost" "total_cost_usd")

# Fallback: if total_input not found, try session-level
[ -z "$total_in" ] && total_in=$(extract_number_after_marker "session" "total_input_tokens")
[ -z "$total_out" ] && total_out=$(extract_number_after_marker "session" "total_output_tokens")

in_fmt=$(format_tokens "${total_in:-0}")
out_fmt=$(format_tokens "${total_out:-0}")

# Total = in + out
total_tok=0
[ -n "$total_in" ] && total_tok=$((total_tok + total_in))
[ -n "$total_out" ] && total_tok=$((total_tok + total_out))
total_fmt=$(format_tokens "$total_tok")

token_segment=""
if [ "$total_tok" -gt 0 ]; then
  token_segment="${total_fmt}tok (in:${in_fmt} out:${out_fmt})"
fi

printf '%s%s%s%s%s%s%s%s%s%s%s' \
  "$model" \
  "$separator" \
  "$branch" \
  "$separator" \
  "$relative_dir" \
  "$separator" \
  "${context_color}${context_segment}${RESET}" \
  "$separator" \
  "5h:${five_hour}${five_hour_suffix}" \
  "$separator" \
  "7d:${seven_day}${seven_day_suffix}"

# Append token counter if available
if [ -n "$token_segment" ]; then
  printf '%s%s' "$separator" "${DIM}${token_segment}${RESET}"
fi
