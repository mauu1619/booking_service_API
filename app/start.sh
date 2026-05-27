#!/bin/bash

# Run migrations
uv run --no-sync alembic upgrade head

# Create admin user
uv run --no-sync python -m app.scripts.create_admin

# Seed database only in dev environment
if [ "$ENV" = "dev" ]; then
    uv run --no-sync python -m app.scripts.seed_db
fi

# Determine if we should use reload
RELOAD_FLAG=""
if [ "$ENV" = "dev" ]; then
    RELOAD_FLAG="--reload"
fi

# Use exec to replace the shell process with uvicorn
exec uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000 $RELOAD_FLAG
