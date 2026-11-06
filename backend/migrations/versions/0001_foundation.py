"""Immutable initial foundation schema; PostgreSQL is authoritative."""
from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE users (
      id uuid PRIMARY KEY, display_name varchar(120) NOT NULL,
      metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL DEFAULT now()
    );
    INSERT INTO users(id,display_name,metadata) VALUES
      ('00000000-0000-4000-8000-000000000001','Local evaluator','{"deployment":"local-single-evaluator"}');
    CREATE TABLE sessions (
      id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
      title varchar(160) NOT NULL CHECK(length(trim(title))>0),
      created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE INDEX sessions_user_updated_idx ON sessions(user_id,updated_at DESC,id);
    CREATE TABLE messages (
      id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
      client_message_id uuid NOT NULL, role varchar(16) NOT NULL CHECK(role IN ('user','assistant')),
      content text NOT NULL CHECK(length(trim(content)) BETWEEN 1 AND 8000),
      status varchar(16) NOT NULL CHECK(status IN ('completed','failed','cancelled')),
      created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(session_id,client_message_id)
    );
    CREATE INDEX messages_session_created_idx ON messages(session_id,created_at,id);
    CREATE TABLE episodes (
      id uuid PRIMARY KEY, source_path text NOT NULL UNIQUE, source_hash varchar(64) NOT NULL,
      title text NOT NULL, guest text, published_on date, video_url text,
      created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE TABLE ingestion_runs (
      id uuid PRIMARY KEY, corpus_revision text NOT NULL, status varchar(16) NOT NULL,
      discovered integer NOT NULL DEFAULT 0 CHECK(discovered>=0), loaded integer NOT NULL DEFAULT 0 CHECK(loaded>=0),
      failed integer NOT NULL DEFAULT 0 CHECK(failed>=0), embedding_model text NOT NULL,
      embedding_dimensions integer NOT NULL CHECK(embedding_dimensions>0),
      created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz
    );
    CREATE TABLE chunks (
      id uuid PRIMARY KEY, episode_id uuid NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
      ingestion_run_id uuid REFERENCES ingestion_runs(id) ON DELETE RESTRICT,
      ordinal integer NOT NULL CHECK(ordinal>=0), version integer NOT NULL CHECK(version>0),
      source_hash varchar(64) NOT NULL, original_text text NOT NULL, search_text text NOT NULL,
      speakers jsonb NOT NULL DEFAULT '[]'::jsonb, start_seconds double precision, end_seconds double precision,
      embedding vector(768), embedding_model text NOT NULL, active boolean NOT NULL DEFAULT false,
      search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english',search_text)) STORED,
      created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(episode_id,version,ordinal),
      CHECK(start_seconds IS NULL OR start_seconds>=0),
      CHECK(end_seconds IS NULL OR start_seconds IS NULL OR end_seconds>=start_seconds)
    );
    CREATE INDEX chunks_episode_active_idx ON chunks(episode_id,active,ordinal);
    CREATE INDEX chunks_search_idx ON chunks USING gin(search_vector);
    CREATE TABLE answer_sources (
      message_id uuid NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
      chunk_id uuid NOT NULL REFERENCES chunks(id) ON DELETE RESTRICT,
      source_label varchar(64) NOT NULL, evidence_text text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(message_id,chunk_id), UNIQUE(message_id,source_label)
    );
    CREATE INDEX answer_sources_chunk_idx ON answer_sources(chunk_id);
    CREATE TABLE artifacts (
      id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
      message_id uuid REFERENCES messages(id) ON DELETE SET NULL,
      type varchar(16) NOT NULL CHECK(type IN ('markdown','html')), title varchar(160) NOT NULL,
      content text NOT NULL, source_metadata jsonb NOT NULL DEFAULT '[]'::jsonb,
      created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE INDEX artifacts_session_created_idx ON artifacts(session_id,created_at,id);
    """)


def downgrade():
    raise RuntimeError("Destructive downgrade is intentionally disabled; restore from a reviewed backup instead")
