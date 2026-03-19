# Codex Skills

Total: 18

| Skill Path | Description |
| --- | --- |
| `skills/.system/openai-docs` | Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations, help choosing the latest model for a use case, or explicit GPT-5.4 upgrade and prompt-upgrade guidance; prioritize OpenAI docs MCP tools, use bundled references only as helper context, and restrict any fallback browsing to official OpenAI domains. |
| `skills/.system/skill-creator` | Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations. |
| `skills/.system/skill-installer` | Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos). |
| `skills/atlas` | macOS-only AppleScript control for the ChatGPT Atlas desktop app. Use only when the user explicitly asks to control Atlas tabs/bookmarks/history on macOS and the \"ChatGPT Atlas\" app is installed; do not trigger for general browser tasks or non-macOS environments. |
| `skills/cct-accessibility-auditor` | Web accessibility specialist for WCAG compliance, ARIA implementation, and inclusive design. Use when auditing websites for accessibility issues, implementing WCAG 2.1 AA/AAA standards, testing with screen readers, or ensuring ADA compliance. Expert in semantic HTML, keyboard navigation, and assistive technology compatibility. |
| `skills/cct-context-window-management` | Strategies for managing LLM context windows including summarization, trimming, routing, and avoiding context rot Use when: context window, token limit, context management, context engineering, long context. |
| `skills/cct-create-plan` | Create a concise plan. Use when a user explicitly asks for a plan related to a coding task. |
| `skills/cct-frontend-design` | Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics. |
| `skills/cct-systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `skills/cct-test-driven-development` | Use when implementing any feature or bugfix, before writing implementation code |
| `skills/cct-web-design-guidelines` | Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices". |
| `skills/gh-address-comments` | Help address review/issue comments on the open GitHub PR for the current branch using gh CLI; verify gh auth first and prompt the user to authenticate if not logged in. |
| `skills/gh-fix-ci` | Use when a user asks to debug or fix failing GitHub PR checks that run in GitHub Actions; use `gh` to inspect checks and logs, summarize failure context, draft a fix plan, and implement only after explicit approval. Treat external providers (for example Buildkite) as out of scope and report only the details URL. |
| `skills/notebooklm` | Complete API for Google NotebookLM - full programmatic access including features not in the web UI. Create notebooks, add sources, generate all artifact types, download in multiple formats. Activates on explicit /notebooklm or intent like "create a podcast about X |
| `skills/notion-knowledge-capture` | Capture conversations and decisions into structured Notion pages; use when turning chats/notes into wiki entries, how-tos, decisions, or FAQs with proper linking. |
| `skills/notion-meeting-intelligence` | Prepare meeting materials with Notion context and Codex research; use when gathering context, drafting agendas/pre-reads, and tailoring materials to attendees. |
| `skills/notion-research-documentation` | Research across Notion and synthesize into structured documentation; use when gathering info from multiple Notion sources to produce briefs, comparisons, or reports with citations. |
| `skills/notion-spec-to-implementation` | Turn Notion specs into implementation plans, tasks, and progress tracking; use when implementing PRDs/feature specs and creating Notion plans + tasks from them. |
