"""Durable reviewed essay workflow, separate from artifact generation/rendering."""
from alembic import op
revision='0004_essays'
down_revision='0003_conversation'
branch_labels=None
depends_on=None


def upgrade():
    op.execute("""
    CREATE TABLE essay_runs (
      id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE RESTRICT,
      user_message_id uuid NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
      assistant_message_id uuid UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
      status text NOT NULL CHECK(status IN ('running','needs_review','completed','failed','cancelled','insufficient_evidence')),
      request jsonb NOT NULL, context_message_ids jsonb NOT NULL DEFAULT '[]', context_text text NOT NULL DEFAULT '',
      outline jsonb, sections jsonb NOT NULL DEFAULT '[]', draft_md text, validation jsonb, review jsonb,
      metadata jsonb NOT NULL DEFAULT '{}', error_code text,
      created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz
    );
    CREATE UNIQUE INDEX essay_one_running_session ON essay_runs(session_id) WHERE status='running';
    CREATE INDEX essay_session_created ON essay_runs(session_id,created_at);
    CREATE TABLE essay_sources (
      run_id uuid NOT NULL REFERENCES essay_runs(id) ON DELETE RESTRICT,
      source_label text NOT NULL CHECK(source_label ~ '^S[1-8]$'),
      chunk_id uuid NOT NULL REFERENCES chunks(id) ON DELETE RESTRICT,
      original_text text NOT NULL, source_metadata jsonb NOT NULL, quote_spans jsonb NOT NULL DEFAULT '[]',
      PRIMARY KEY(run_id,source_label)
    );
    """)


def downgrade():raise RuntimeError('Destructive essay downgrade requires a separately reviewed backup/migration')
