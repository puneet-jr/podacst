"""Persist bounded conversation operations and immutable citation snapshots."""
from alembic import op

revision = '0003_conversation'
down_revision = '0002_ingestion'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE answer_runs (
      id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE RESTRICT,
      user_message_id uuid NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
      assistant_message_id uuid UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
      status varchar(16) NOT NULL CHECK(status IN ('running','completed','failed','cancelled')),
      attempt integer NOT NULL DEFAULT 1 CHECK(attempt>0), retrieval_mode text NOT NULL CHECK(retrieval_mode='hybrid'),
      source_path text, resolved_query text NOT NULL, context_message_ids jsonb NOT NULL DEFAULT '[]',
      metadata jsonb NOT NULL DEFAULT '{}', output jsonb, error_code text,
      started_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz
    );
    CREATE UNIQUE INDEX answer_runs_one_running_session ON answer_runs(session_id) WHERE status='running';
    ALTER TABLE answer_sources ADD COLUMN source_metadata jsonb NOT NULL DEFAULT '{}';
    ALTER TABLE answer_sources ADD COLUMN quote_spans jsonb NOT NULL DEFAULT '[]';
    CREATE INDEX answer_runs_session_started ON answer_runs(session_id,started_at);
    """)


def downgrade():
    raise RuntimeError('Destructive conversation downgrade requires a separately reviewed backup/migration')
