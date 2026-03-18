# Memory

## Overview

This setup uses two distinct memory tracks:

- a legacy local memory stack in `~/.claude-mem`
- an active hybrid MCP memory stack in `~/.claude-mem-hybrid`

The repository publishes the architecture and configuration shape of both, but not the stored memories.

## Legacy `.claude-mem`

The older stack stores conversational and observational memory locally.

### Published

- `.claude-mem/settings.template.json`
- `.claude-mem/legacy-plugin/plugin.json`
- `.claude-mem/legacy-plugin/mcp.json`

### Not published

- SQLite databases
- Chroma/vector indexes
- worker state
- logs
- observer sessions

### Observed storage shape

The SQLite schema contains:

- `sdk_sessions`
- `user_prompts`
- `pending_messages`
- `observations`
- `session_summaries`
- FTS virtual tables for prompts, observations, and summaries

Observed counts at export time:

- `sdk_sessions`: 101
- `user_prompts`: 689
- `observations`: 3928
- `session_summaries`: 495
- `pending_messages`: 99

This means the legacy system keeps:

- session registry
- prompt history
- synthesized observations
- session summaries
- full-text search indexes

In practice it behaves like a local notebook plus retrieval layer backed by SQLite and vector storage.

The legacy plugin metadata shows:

- plugin name: `claude-mem`
- version: `10.4.3`
- repository: `thedotmack/claude-mem`
- MCP server name: `mcp-search`
- transport: stdio

## Hybrid `.claude-mem-hybrid`

This is the current MCP-facing memory server.

### Runtime architecture

- PostgreSQL stores durable memory rows
- Redis caches search results and keeps a recent-memory buffer
- `mcp_memory_server.py` exposes the tools over stdio MCP

### MCP tools

- `memory_store`
- `memory_search`
- `memory_recent`
- `memory_delete`
- `memory_stats`

### PostgreSQL schema

The `memories` table contains:

- `id`
- `content`
- `tags`
- `source`
- `created_at`
- `updated_at`

Indexes:

- descending index on `created_at`
- GIN on `tags`
- `pg_trgm` GIN index on `content`

### Redis behavior

The server uses Redis for:

- cached search results keyed as `mem:search:<sha1>`
- search-key registry `mem:search_keys`
- recent-memory list `mem:recent`

Search cache TTL is 120 seconds. A new stored memory invalidates cached searches and prepends the memory to the recent list.

### Publication boundary

Published:

- server code
- compose file
- schema
- launcher
- README

Excluded:

- `data/postgres/`
- `data/redis/`
- `server.log`

That keeps the repo reproducible without leaking real memory contents.
