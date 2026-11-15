"""Run Alembic through the connection supplied by manage_catalog.py."""

from alembic import context

from models import Base


context.configure(connection=context.config.attributes["connection"], target_metadata=Base.metadata)
with context.begin_transaction():
    context.run_migrations()
