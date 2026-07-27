#!/bin/bash
set -e

# Run database migrations
echo "Running database migrations..."
alembic -c backend/alembic.ini upgrade head

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A backend.worker.celery_app worker --loglevel=info &

# Start Telegram Bot in background
echo "Starting Telegram Bot..."
python -m backend.bot.main &

# Start FastAPI server in foreground
echo "Starting FastAPI server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
