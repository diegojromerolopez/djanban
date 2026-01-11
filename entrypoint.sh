#!/bin/bash

# Wait for database to be ready (already handled by depends_on healthcheck in compose but good practice)
echo "Waiting for database..."

# Run migrations
echo "Running migrations..."
python src/manage.py migrate --noinput

# Start server
echo "Starting server..."
python src/manage.py runserver 0.0.0.0:8000
