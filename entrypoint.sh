#!/bin/sh
set -e

APP_ROLE="${APP_ROLE:-web}"

# Database host/port: use INTERNAL_DATABASE_URL or DATABASE_URL (Render), else DB_HOST/DB_PORT (local Docker)
if [ -n "${INTERNAL_DATABASE_URL:-$DATABASE_URL}" ]; then
  _out=$(python -c "
import os
from urllib.parse import urlparse
url = os.environ.get('INTERNAL_DATABASE_URL') or os.environ.get('DATABASE_URL') or ''
u = urlparse(url)
print('DB_HOST=%s' % (u.hostname or ''))
print('DB_PORT=%s' % (u.port or 5432))
" 2>/dev/null) && eval "$_out" || true
fi
if [ -z "$DB_HOST" ]; then
  : "${DB_HOST:=db}"
  : "${DB_PORT:=5432}"
  echo "DATABASE_URL not set; using ${DB_HOST}:${DB_PORT} (local Docker)."
else
  : "${DB_PORT:=5432}"
  echo "Using database from DATABASE_URL: host=${DB_HOST} port=${DB_PORT}"
fi

# Default command if none is provided (matches Dockerfile CMD - gunicorn for production)
if [ "$#" -eq 0 ]; then
  set -- /bin/sh -c "exec gunicorn config.wsgi:application -b 0.0.0.0:${PORT:-8000} --workers 2"
fi

# Wait for the database to be reachable
if [ -n "$DB_HOST" ]; then
  if [ "$DB_HOST" = "db" ] && [ -n "${PORT:-}" ]; then
    echo "WARNING: DATABASE_URL is not set but PORT is (likely Render). Link the PostgreSQL database to this service and set DATABASE_URL."
  fi
  echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
  until nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 1
  done
  echo "Database is up"
fi

if [ "$APP_ROLE" = "web" ]; then
  echo "Applying database migrations..."
  python manage.py migrate --noinput

  echo "Collecting static files..."
  python manage.py collectstatic --noinput
else
  echo "Skipping migrations and collectstatic for APP_ROLE=${APP_ROLE}."
fi

# Start Django development server (or any other command passed in)
echo "Starting application..."
exec "$@"
