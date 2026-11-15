"""Database engine configuration shared by the API and migration command."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url


def catalog_engine(database_url):
    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")
    options = {"pool_pre_ping": True, "hide_parameters": True}
    if url.get_backend_name() == "postgresql":
        options["connect_args"] = {"connect_timeout": 10}
    engine = create_engine(url, **options)
    if url.get_backend_name() == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    return engine
