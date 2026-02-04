"""
Alembic Environment Configuration

This module is used by Alembic to configure the migration environment.
It connects to the database and provides the target metadata for autogenerate.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add parent directory to path to import application modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import database models and session
from database.models import Base
from database.session import get_database_url

# =============================================================================
# Alembic Config Object
# =============================================================================

# This is the Alembic Config object, which provides access to values within
# the .ini file in use.
config = context.config

# Override sqlalchemy.url from DATABASE_URL environment variable
# This allows us to use the same database configuration as the application
database_url = get_database_url()
if not database_url.startswith("sqlite"):  # Unmask for actual connection
    # For Alembic, we need the actual URL, not the masked one
    database_url = os.getenv("DATABASE_URL", "sqlite:///./conversations.db")

config.set_main_option("sqlalchemy.url", database_url)

# =============================================================================
# Logging Configuration
# =============================================================================

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite support
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    # Handle SQLite special requirements
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool if database_url.startswith("sqlite") else pool.QueuePool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite ALTER TABLE support
        )

        with context.begin_transaction():
            context.run_migrations()


# =============================================================================
# Main Entry Point
# =============================================================================

# Determine if we're running in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
