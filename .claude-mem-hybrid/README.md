# Claude Hybrid Memory (Redis + PostgreSQL)

Stack local para memória persistente e cache de busca do Claude via MCP.

## Arquitetura
- PostgreSQL: persistência principal de memórias.
- Redis: cache de buscas e buffer de recentes.
- MCP server (`mcp_memory_server.py`): expõe ferramentas para o Claude.

## Subir stack
```bash
cd ~/.claude-mem-hybrid
docker compose up -d
```

## Registrar MCP no Claude Code
```bash
"claude" mcp add mem-hybrid -- \
  python3 ~/.claude-mem-hybrid/mcp_memory_server.py
```

## Remover MCP
```bash
"claude" mcp remove mem-hybrid
```

## Derrubar stack
```bash
cd ~/.claude-mem-hybrid
docker compose down
```
