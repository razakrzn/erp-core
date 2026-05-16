FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for Python packages and entrypoint DB readiness checks.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libpq-dev \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN mkdir -p /var/www/media /var/www/static && \
    ln -sfn /var/www/media /app/media

EXPOSE 3002

# Keep uploads out of image layers; mount persistent storage at runtime.
VOLUME ["/var/www/media"]

CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:3002", "--workers", "2", "--timeout", "120", "--log-file", "-"]
