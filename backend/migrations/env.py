from alembic import context
from backend.app.config import load_settings
from backend.app.db import make_engine

engine = make_engine(load_settings())
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()
engine.dispose()
