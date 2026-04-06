#!/bin/bash

uv run alembic upgrade head

uv run python -m app.scripts.create_admin

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload