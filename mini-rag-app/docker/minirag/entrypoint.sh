#!/bin/sh
set -e
echo "Running database migrations..."
cd /app/models/db_scehmes/minirag/
alembic upgrade head
cd /app
echo "Starting the MiniRAG application..."

# Run CMD from Dockerfile (uvicorn)
exec "$@"