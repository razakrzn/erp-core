FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for Python packages and database drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libpq-dev \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Setup media and static directories
RUN mkdir -p /var/www/media /var/www/static && \
    ln -sfn /var/www/media /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the application port
EXPOSE 8002

# Keep uploads out of image layers; mount persistent storage at runtime
VOLUME ["/var/www/media"]

# Default command using gunicorn
CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--log-file", "-"]
