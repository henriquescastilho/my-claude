#!/usr/bin/env python3
import hashlib
import json
import os
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import psycopg


PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "mem-hybrid"
SERVER_VERSION = "0.1.0"
LOG_FILE = os.environ.get("MEMORY_SERVER_LOG", os.path.expanduser("~/.claude-mem-hybrid/server.log"))


def log_line(message: str) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{utc_now_iso()} {message}\n")
    except Exception:
        pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryRow:
    id: int
    content: str
    tags: list[str]
    source: str | None
    created_at: str


class PostgresStore:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = psycopg.connect(dsn, autocommit=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                  id BIGSERIAL PRIMARY KEY,
                  content TEXT NOT NULL,
                  tags TEXT[] NOT NULL DEFAULT '{}',
                  source TEXT,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories (created_at DESC)"
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN (tags)")
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_content_trgm ON memories USING GIN (content gin_trgm_ops)"
            )

    def insert(self, content: str, tags: list[str], source: str | None) -> MemoryRow:
        clean_tags = [t.strip() for t in tags if t and t.strip()]
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memories (content, tags, source)
                VALUES (%s, %s, %s)
                RETURNING id, content, tags, source, created_at
                """,
                (content, clean_tags, source),
            )
            row = cur.fetchone()
        return MemoryRow(
            id=row[0],
            content=row[1],
            tags=list(row[2] or []),
            source=row[3],
            created_at=row[4].isoformat(),
        )

    def search(self, query: str, limit: int) -> list[MemoryRow]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, content, tags, source, created_at
                FROM memories
                WHERE content ILIKE %s
                   OR EXISTS (
                        SELECT 1 FROM unnest(tags) AS t
                        WHERE t ILIKE %s
                   )
                ORDER BY
                  similarity(content, %s) DESC,
                  created_at DESC
                LIMIT %s
                """,
                (f"%{query}%", f"%{query}%", query, limit),
            )
            rows = cur.fetchall()
        return [
            MemoryRow(
                id=r[0],
                content=r[1],
                tags=list(r[2] or []),
                source=r[3],
                created_at=r[4].isoformat(),
            )
            for r in rows
        ]

    def recent(self, limit: int) -> list[MemoryRow]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, content, tags, source, created_at
                FROM memories
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        return [
            MemoryRow(
                id=r[0],
                content=r[1],
                tags=list(r[2] or []),
                source=r[3],
                created_at=r[4].isoformat(),
            )
            for r in rows
        ]

    def delete(self, memory_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM memories WHERE id = %s", (memory_id,))
            return cur.rowcount > 0

    def stats(self) -> dict[str, Any]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM memories")
            total = cur.fetchone()[0]
            cur.execute("SELECT max(created_at) FROM memories")
            latest = cur.fetchone()[0]
        return {
            "total_memories": total,
            "latest_memory_at": latest.isoformat() if latest else None,
        }


class RedisCache:
    def __init__(self, redis_url: str):
        self.url = redis_url
        parsed = urlparse(redis_url)
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 6379
        self.password = parsed.password
        self.db = int((parsed.path or "/0").lstrip("/") or 0)
        self.sock = socket.create_connection((self.host, self.port), timeout=2)
        if self.password:
            self._send(["AUTH", self.password])
        if self.db:
            self._send(["SELECT", str(self.db)])
        self._send(["PING"])

    def _pack(self, cmd: list[str]) -> bytes:
        parts = [f"*{len(cmd)}\r\n".encode()]
        for arg in cmd:
            data = arg.encode("utf-8")
            parts.append(f"${len(data)}\r\n".encode())
            parts.append(data + b"\r\n")
        return b"".join(parts)

    def _readline(self) -> bytes:
        buf = bytearray()
        while True:
            ch = self.sock.recv(1)
            if not ch:
                raise ConnectionError("Redis connection closed")
            buf.extend(ch)
            if len(buf) >= 2 and buf[-2:] == b"\r\n":
                return bytes(buf[:-2])

    def _read_resp(self) -> Any:
        line = self._readline()
        prefix = line[:1]
        payload = line[1:]
        if prefix == b"+":
            return payload.decode("utf-8")
        if prefix == b"-":
            raise RuntimeError(payload.decode("utf-8"))
        if prefix == b":":
            return int(payload)
        if prefix == b"$":
            length = int(payload)
            if length == -1:
                return None
            data = b""
            remaining = length + 2
            while remaining > 0:
                chunk = self.sock.recv(remaining)
                if not chunk:
                    raise ConnectionError("Redis connection closed while reading bulk string")
                data += chunk
                remaining -= len(chunk)
            return data[:-2].decode("utf-8")
        if prefix == b"*":
            count = int(payload)
            if count == -1:
                return None
            return [self._read_resp() for _ in range(count)]
        raise RuntimeError("Unknown RESP response type")

    def _send(self, cmd: list[str]) -> Any:
        self.sock.sendall(self._pack(cmd))
        return self._read_resp()

    def get(self, key: str) -> str | None:
        value = self._send(["GET", key])
        return value if isinstance(value, str) else None

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self._send(["SETEX", key, str(ttl_seconds), value])

    def sadd(self, key: str, value: str) -> None:
        self._send(["SADD", key, value])

    def smembers(self, key: str) -> list[str]:
        values = self._send(["SMEMBERS", key]) or []
        return [v for v in values if isinstance(v, str)]

    def delete_many(self, keys: list[str]) -> None:
        if keys:
            self._send(["DEL", *keys])

    def lpush(self, key: str, value: str) -> None:
        self._send(["LPUSH", key, value])

    def ltrim(self, key: str, start: int, end: int) -> None:
        self._send(["LTRIM", key, str(start), str(end)])


class HybridMemory:
    def __init__(self, pg_dsn: str, redis_url: str):
        self.store = PostgresStore(pg_dsn)
        self.cache: RedisCache | None
        try:
            self.cache = RedisCache(redis_url)
        except Exception:
            self.cache = None

    def _search_cache_key(self, query: str, limit: int) -> str:
        digest = hashlib.sha1(f"{query}|{limit}".encode("utf-8")).hexdigest()
        return f"mem:search:{digest}"

    def _invalidate_search_cache(self) -> None:
        if not self.cache:
            return
        keys = self.cache.smembers("mem:search_keys")
        if keys:
            self.cache.delete_many(keys)

    def store_memory(self, content: str, tags: list[str], source: str | None) -> MemoryRow:
        row = self.store.insert(content, tags, source)
        if self.cache:
            payload = json.dumps(
                {
                    "id": row.id,
                    "content": row.content,
                    "tags": row.tags,
                    "source": row.source,
                    "created_at": row.created_at,
                }
            )
            self.cache.lpush("mem:recent", payload)
            self.cache.ltrim("mem:recent", 0, 199)
            self._invalidate_search_cache()
        return row

    def search_memory(self, query: str, limit: int) -> tuple[list[MemoryRow], bool]:
        if self.cache:
            key = self._search_cache_key(query, limit)
            cached = self.cache.get(key)
            if cached:
                rows = [MemoryRow(**item) for item in json.loads(cached)]
                return rows, True
        rows = self.store.search(query, limit)
        if self.cache:
            key = self._search_cache_key(query, limit)
            self.cache.setex(
                key,
                120,
                json.dumps([row.__dict__ for row in rows]),
            )
            self.cache.sadd("mem:search_keys", key)
        return rows, False

    def recent_memory(self, limit: int) -> list[MemoryRow]:
        return self.store.recent(limit)

    def delete_memory(self, memory_id: int) -> bool:
        deleted = self.store.delete(memory_id)
        if deleted and self.cache:
            self._invalidate_search_cache()
        return deleted

    def stats(self) -> dict[str, Any]:
        out = self.store.stats()
        out["redis_cache"] = "enabled" if self.cache else "disabled"
        out["server_time"] = utc_now_iso()
        return out


class McpServer:
    def __init__(self, memory: HybridMemory):
        self.memory = memory

    def run(self) -> None:
        while True:
            msg = self._read_message()
            if msg is None:
                break
            self._handle(msg)

    def _read_message(self) -> dict[str, Any] | None:
        line = sys.stdin.buffer.readline()
        if not line:
            return None

        stripped = line.strip()
        if not stripped:
            return None

        # Claude Code stdio MCP transport sends newline-delimited JSON-RPC.
        if not stripped.lower().startswith(b"content-length:"):
            return json.loads(stripped.decode("utf-8"))

        # Compatibility fallback for Content-Length framed payloads.
        headers: dict[str, str] = {}
        while True:
            text = line.decode("utf-8").strip()
            if text:
                if ":" in text:
                    key, value = text.split(":", 1)
                    headers[key.strip().lower()] = value.strip()
            else:
                break
            line = sys.stdin.buffer.readline()
            if not line:
                return None
            if line in (b"\r\n", b"\n"):
                break

        length = int(headers.get("content-length", "0"))
        if length <= 0:
            return None
        payload = sys.stdin.buffer.read(length)
        return json.loads(payload.decode("utf-8"))

    def _send(self, obj: dict[str, Any]) -> None:
        data = json.dumps(obj, ensure_ascii=True).encode("utf-8")
        sys.stdout.buffer.write(data + b"\n")
        sys.stdout.buffer.flush()

    def _result(self, req_id: Any, result: dict[str, Any]) -> None:
        self._send({"jsonrpc": "2.0", "id": req_id, "result": result})

    def _error(self, req_id: Any, code: int, message: str) -> None:
        self._send(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": code, "message": message},
            }
        )

    def _handle(self, msg: dict[str, Any]) -> None:
        method = msg.get("method")
        req_id = msg.get("id")
        log_line(f"recv method={method!r} id={req_id!r}")

        try:
            if method == "initialize":
                self._result(
                    req_id,
                    {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    },
                )
                return

            if method == "notifications/initialized":
                return

            if method == "ping":
                self._result(req_id, {})
                return

            if method == "tools/list":
                self._result(req_id, {"tools": self._tools_schema()})
                return

            if method == "tools/call":
                params = msg.get("params", {})
                name = params.get("name")
                arguments = params.get("arguments", {})
                self._result(req_id, self._call_tool(name, arguments))
                return

            if req_id is not None:
                self._error(req_id, -32601, f"Method not found: {method}")
        except Exception as exc:
            log_line(f"error method={method!r} id={req_id!r} err={exc!r}")
            if req_id is not None:
                self._error(req_id, -32000, f"Internal error: {exc}")

    def _tools_schema(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "memory_store",
                "description": "Persist an important memory in PostgreSQL and update Redis cache.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": [],
                        },
                        "source": {"type": "string"},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "memory_search",
                "description": "Search memories by semantic-like text match over content and tags.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 8},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "memory_recent",
                "description": "Return the most recently stored memories.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}
                    },
                },
            },
            {
                "name": "memory_delete",
                "description": "Delete a memory by id.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"id": {"type": "integer", "minimum": 1}},
                    "required": ["id"],
                },
            },
            {
                "name": "memory_stats",
                "description": "Show memory store stats and cache status.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    def _call_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        if name == "memory_store":
            content = str(args.get("content", "")).strip()
            if not content:
                return self._tool_error("`content` is required")
            tags = args.get("tags") or []
            if not isinstance(tags, list):
                return self._tool_error("`tags` must be an array of strings")
            source = args.get("source")
            row = self.memory.store_memory(content, [str(t) for t in tags], str(source) if source else None)
            return self._tool_ok(
                {
                    "id": row.id,
                    "content": row.content,
                    "tags": row.tags,
                    "source": row.source,
                    "created_at": row.created_at,
                }
            )

        if name == "memory_search":
            query = str(args.get("query", "")).strip()
            if not query:
                return self._tool_error("`query` is required")
            limit = int(args.get("limit", 8))
            limit = max(1, min(limit, 50))
            rows, cache_hit = self.memory.search_memory(query, limit)
            return self._tool_ok(
                {
                    "query": query,
                    "limit": limit,
                    "cache_hit": cache_hit,
                    "results": [r.__dict__ for r in rows],
                }
            )

        if name == "memory_recent":
            limit = int(args.get("limit", 10))
            limit = max(1, min(limit, 50))
            rows = self.memory.recent_memory(limit)
            return self._tool_ok({"limit": limit, "results": [r.__dict__ for r in rows]})

        if name == "memory_delete":
            mem_id = int(args.get("id", 0))
            if mem_id <= 0:
                return self._tool_error("`id` must be a positive integer")
            deleted = self.memory.delete_memory(mem_id)
            return self._tool_ok({"id": mem_id, "deleted": deleted})

        if name == "memory_stats":
            return self._tool_ok(self.memory.stats())

        return self._tool_error(f"Unknown tool: {name}")

    def _tool_ok(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = json.dumps(payload, ensure_ascii=True, indent=2)
        return {
            "isError": False,
            "content": [{"type": "text", "text": text}],
            "structuredContent": payload,
        }

    def _tool_error(self, message: str) -> dict[str, Any]:
        return {
            "isError": True,
            "content": [{"type": "text", "text": message}],
        }


def main() -> int:
    pg_dsn = os.environ.get(
        "MEMORY_POSTGRES_DSN",
        "postgresql://claude@127.0.0.1:54329/claude_memory",
    )
    redis_url = os.environ.get("MEMORY_REDIS_URL", "redis://127.0.0.1:6389/0")

    for _ in range(30):
        try:
            memory = HybridMemory(pg_dsn, redis_url)
            log_line("startup connected postgres; redis=" + ("enabled" if memory.cache else "disabled"))
            break
        except Exception as exc:
            log_line(f"startup retry due to: {exc!r}")
            time.sleep(1)
    else:
        print("Failed to connect to PostgreSQL after 30 attempts", file=sys.stderr)
        log_line("startup failed after retries")
        return 1

    server = McpServer(memory)
    log_line("server ready")
    server.run()
    log_line("server stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
