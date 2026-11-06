"""Versioned evidence, resumable ingestion outcomes and index identity."""
from alembic import op

revision = "0002_ingestion"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    ALTER TABLE episodes ADD COLUMN current_version integer;
    ALTER TABLE episodes ADD COLUMN deleted_at timestamptz;
    CREATE TABLE episode_versions (
      episode_id uuid NOT NULL REFERENCES episodes(id) ON DELETE RESTRICT,
      version integer NOT NULL CHECK(version>0), source_path text NOT NULL, source_hash varchar(64) NOT NULL,
      corpus_revision text NOT NULL, original_text text NOT NULL, metadata jsonb NOT NULL,
      parser_version text NOT NULL, chunker_version text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(episode_id,version)
    );
    ALTER TABLE episodes ADD CONSTRAINT episodes_current_version_fk
      FOREIGN KEY(id,current_version) REFERENCES episode_versions(episode_id,version) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE chunks ADD CONSTRAINT chunks_version_fk
      FOREIGN KEY(episode_id,version) REFERENCES episode_versions(episode_id,version) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE chunks ADD COLUMN char_start integer NOT NULL DEFAULT 0;
    ALTER TABLE chunks ADD COLUMN char_end integer NOT NULL DEFAULT 0;
    ALTER TABLE chunks ADD COLUMN line_start integer NOT NULL DEFAULT 1;
    ALTER TABLE chunks ADD COLUMN line_end integer NOT NULL DEFAULT 1;
    ALTER TABLE chunks ADD COLUMN estimated_tokens integer NOT NULL DEFAULT 0;
    ALTER TABLE chunks ADD COLUMN sponsor boolean NOT NULL DEFAULT false;
    ALTER TABLE chunks ADD COLUMN embedding_digest text;
    ALTER TABLE chunks ADD COLUMN corpus_revision text;
    ALTER TABLE chunks ADD CONSTRAINT chunks_span_check CHECK(char_start>=0 AND char_end>=char_start AND line_start>0 AND line_end>=line_start);
    CREATE UNIQUE INDEX chunks_one_active_ordinal ON chunks(episode_id,ordinal) WHERE active;
    ALTER TABLE ingestion_runs ADD COLUMN selected integer NOT NULL DEFAULT 0;
    ALTER TABLE ingestion_runs ADD COLUMN skipped integer NOT NULL DEFAULT 0;
    ALTER TABLE ingestion_runs ADD COLUMN deleted integer NOT NULL DEFAULT 0;
    ALTER TABLE ingestion_runs ADD COLUMN embedding_digest text;
    ALTER TABLE ingestion_runs ADD COLUMN pipeline_version text;
    ALTER TABLE ingestion_runs ADD COLUMN source_url text;
    ALTER TABLE ingestion_runs ADD COLUMN source_kind varchar(16) NOT NULL DEFAULT 'corpus';
    ALTER TABLE ingestion_runs ADD COLUMN manifest_complete boolean NOT NULL DEFAULT false;
    ALTER TABLE ingestion_runs ADD COLUMN last_error_code text;
    ALTER TABLE ingestion_runs ADD COLUMN heartbeat_at timestamptz NOT NULL DEFAULT now();
    CREATE TABLE ingestion_items (
      run_id uuid NOT NULL REFERENCES ingestion_runs(id) ON DELETE RESTRICT,
      source_path text NOT NULL, source_hash varchar(64), status varchar(16) NOT NULL,
      episode_id uuid REFERENCES episodes(id) ON DELETE RESTRICT,
      chunks integer NOT NULL DEFAULT 0, error_code text, warnings jsonb NOT NULL DEFAULT '[]'::jsonb,
      updated_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(run_id,source_path)
    );
    CREATE INDEX ingestion_items_status_idx ON ingestion_items(run_id,status);
    CREATE TABLE knowledge_config (
      singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),
      source_url text NOT NULL, embedding_model text NOT NULL, embedding_digest text NOT NULL,
      dimensions integer NOT NULL CHECK(dimensions=768), document_prefix text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now()
    );
    """)


def downgrade():
    raise RuntimeError("Destructive evidence downgrade requires a separately reviewed data migration")
