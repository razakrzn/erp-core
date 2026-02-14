#!/bin/sh
set -e

# Default database host/port if not provided
: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"

# Default command if none is provided (matches Dockerfile CMD - gunicorn for production)
if [ "$#" -eq 0 ]; then
  set -- /bin/sh -c "exec gunicorn config.wsgi:application -b 0.0.0.0:${PORT:-8000} --workers 2"
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