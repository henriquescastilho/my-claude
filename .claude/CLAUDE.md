# Execution Defaults (Lean Mode)

## Objective
Use less context per turn and rely on persisted memory for continuity.

## Memory policy (`mem-hybrid`)
1. Before deep analysis, call `memory_search` with a focused query for prior decisions/work.
2. Only keep the minimum active context needed for the current step.
3. After a meaningful decision/fix, call `memory_store` with concise `content` and 2-5 tags.
4. Prefer `memory_recent` over large recap requests.

## Output policy
1. Think through the full plan before acting; keep the visible summary concise only when brevity does not hide important detail.
2. Do not omit dependencies, risks, edge cases, or validation needs just to stay brief.
3. Avoid repeating already accepted decisions; reference memory instead.
4. Use small, verifiable execution steps after the full plan is coherent.

## Orchestration policy
1. For any request beyond a trivial fact lookup or one-command action, operate in orchestrated mode.
2. Build a complete execution plan before implementation. Cover workstreams, dependencies, assumptions, risks, rollback, acceptance criteria, and validation.
3. Present a concise plan summary by default, but preserve complete internal planning and expand it whenever the task complexity justifies it.
4. When registered agents are available, delegate each non-trivial workstream to the best-fit subagent instead of keeping all specialist work in the main thread.
5. Maintain a master context ledger: objective, constraints, accepted decisions, relevant files, dependencies, open questions, and subagent outputs.
6. Re-brief downstream subagents with the latest accepted context so execution stays logical and coherent across handoffs.
7. The orchestrator owns scope, prioritization, conflict resolution, and final synthesis.
