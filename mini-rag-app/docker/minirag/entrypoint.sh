#!/bin/sh
set -e
echo "Running database migrations..."
cd /app/models/db_schema/minirag/
alembic upgrade head
cd /app
echo "Starting the MiniRAG application..."