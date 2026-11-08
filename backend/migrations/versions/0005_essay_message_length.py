"""Permit bounded long assistant essays while retaining the user message limit."""
from alembic import op
revision='0005_essay_message_length'
down_revision='0004_essays'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('ALTER TABLE messages DROP CONSTRAINT messages_content_check')
    op.execute("ALTER TABLE messages ADD CONSTRAINT messages_content_check CHECK(length(trim(content)) BETWEEN 1 AND CASE WHEN role='assistant' THEN 32768 ELSE 8000 END)")

def downgrade():
    raise RuntimeError('Long saved essays cannot be destructively narrowed without review')
