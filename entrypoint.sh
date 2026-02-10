#!/bin/sh
set -e

# Default database host/port if not provided
: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"

# Default command if none is provided (matches Dockerfile CMD)
if [ "$#" -eq 0 ]; then
  set -- python manage.py runserver 0.0.0.0:8000
fi

# Optional: wait for the database to be ready
echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is up"

# Run migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files (optional, if you use staticfiles)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Start Django development server (or any other command passed in)
echo "Starting application..."
exec "$@"