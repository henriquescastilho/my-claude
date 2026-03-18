# Agents

Total: 29

| Name | Model | Memory | File | Description |
| --- | --- | --- | --- | --- |
| `backend-architect` | `sonnet` | `user` | `backend-architect.md` | Designs robust backend architecture, APIs, domain boundaries, and data models for scalable systems. |
| `cct-fullstack-developer` | `sonnet` | `-` | `cct-fullstack-developer.md` | Builds production features end-to-end across database, backend APIs, and frontend UI layers. |
| `cct-incident-responder` | `opus` | `-` | `cct-incident-responder.md` | Leads production incident triage, containment, root-cause analysis, and safe recovery execution. |
| `cct-test-runner` | `sonnet` | `-` | `cct-test-runner.md` | Runs test suites, analyzes failures, and reports precise fixes with minimal noise. |
| `code-reviewer` | `sonnet` | `user` | `code-reviewer.md` | Performs rigorous code review focused on bugs, regressions, security, and maintainability. |
| `finops-cost-guard` | `sonnet` | `user` | `finops-cost-guard.md` | Optimizes infrastructure and AI usage cost with practical, measurable engineering trade-offs. |
| `frontend-ux-engineer` | `sonnet` | `user` | `frontend-ux-engineer.md` | Designs and implements accessible, performant frontend experiences from UX flows to components. |
| `gsd-codebase-mapper` | `-` | `-` | `gsd-codebase-mapper.md` | Explores codebase and writes structured analysis documents. Spawned by map-codebase with a focus area (tech, arch, quality, concerns). Writes documents directly to reduce orchestrator context load. |
| `gsd-debugger` | `-` | `-` | `gsd-debugger.md` | Investigates bugs using scientific method, manages debug sessions, handles checkpoints. Spawned by /gsd:debug orchestrator. |
| `gsd-executor` | `-` | `-` | `gsd-executor.md` | Executes GSD plans with atomic commits, deviation handling, checkpoint protocols, and state management. Spawned by execute-phase orchestrator or execute-plan command. |
| `gsd-integration-checker` | `-` | `-` | `gsd-integration-checker.md` | Verifies cross-phase integration and E2E flows. Checks that phases connect properly and user workflows complete end-to-end. |
| `gsd-nyquist-auditor` | `-` | `-` | `gsd-nyquist-auditor.md` | Fills Nyquist validation gaps by generating tests and verifying coverage for phase requirements |
| `gsd-phase-researcher` | `-` | `-` | `gsd-phase-researcher.md` | Researches how to implement a phase before planning. Produces RESEARCH.md consumed by gsd-planner. Spawned by /gsd:plan-phase orchestrator. |
| `gsd-plan-checker` | `-` | `-` | `gsd-plan-checker.md` | Verifies plans will achieve phase goal before execution. Goal-backward analysis of plan quality. Spawned by /gsd:plan-phase orchestrator. |
| `gsd-planner` | `-` | `-` | `gsd-planner.md` | Creates executable phase plans with task breakdown, dependency analysis, and goal-backward verification. Spawned by /gsd:plan-phase orchestrator. |
| `gsd-project-researcher` | `-` | `-` | `gsd-project-researcher.md` | Researches domain ecosystem before roadmap creation. Produces files in .planning/research/ consumed during roadmap creation. Spawned by /gsd:new-project or /gsd:new-milestone orchestrators. |
| `gsd-research-synthesizer` | `-` | `-` | `gsd-research-synthesizer.md` | Synthesizes research outputs from parallel researcher agents into SUMMARY.md. Spawned by /gsd:new-project after 4 researcher agents complete. |
| `gsd-roadmapper` | `-` | `-` | `gsd-roadmapper.md` | Creates project roadmaps with phase breakdown, requirement mapping, success criteria derivation, and coverage validation. Spawned by /gsd:new-project orchestrator. |
| `gsd-ui-auditor` | `-` | `-` | `gsd-ui-auditor.md` | Retroactive 6-pillar visual audit of implemented frontend code. Produces scored UI-REVIEW.md. Spawned by /gsd:ui-review orchestrator. |
| `gsd-ui-checker` | `-` | `-` | `gsd-ui-checker.md` | Validates UI-SPEC.md design contracts against 6 quality dimensions. Produces BLOCK/FLAG/PASS verdicts. Spawned by /gsd:ui-phase orchestrator. |
| `gsd-ui-researcher` | `-` | `-` | `gsd-ui-researcher.md` | Produces UI-SPEC.md design contract for frontend phases. Reads upstream artifacts, detects design system state, asks only unanswered questions. Spawned by /gsd:ui-phase orchestrator. |
| `gsd-verifier` | `-` | `-` | `gsd-verifier.md` | Verifies phase goal achievement through goal-backward analysis. Checks codebase delivers what phase promised, not just that tasks completed. Creates VERIFICATION.md report. |
| `infra-sre-lead` | `sonnet` | `user` | `infra-sre-lead.md` | Owns infrastructure reliability, CI/CD, observability, scaling, and operational resilience. |
| `qa-test-engineer` | `sonnet` | `user` | `qa-test-engineer.md` | Defines test strategy, validates critical flows, and prevents regressions before release. |
| `repo-curator` | `sonnet` | `user` | `repo-curator.md` | Improves repository health, standards, contribution workflow, and long-term maintainability. |
| `security-lead` | `sonnet` | `user` | `security-lead.md` | Hardens application and infrastructure security across auth, data, secrets, and runtime defenses. |
| `team-orchestrator` | `opus` | `user` | `team-orchestrator.md` | End-to-end engineering orchestrator for one-shot prompts across backend, frontend, infrastructure, security, QA, and delivery. |
| `tech-writer-runbooks` | `sonnet` | `user` | `tech-writer-runbooks.md` | Produces clear technical docs and runbooks for development, operations, and incident response. |
| `web-researcher` | `sonnet` | `user` | `web-researcher.md` | Collects and validates up-to-date technical references from primary official sources. |
