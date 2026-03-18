CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS memories (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  tags TEXT[] NOT NULL DEFAULT '{}',
  source TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_memories_content_trgm ON memories USING GIN (content gin_trgm_ops);

CREATE OR REPLACE FUNCTION set_updated_at_memories()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_updated_at_memories ON memories;
CREATE TRIGGER trg_set_updated_at_memories
BEFORE UPDATE ON memories
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_memories();
