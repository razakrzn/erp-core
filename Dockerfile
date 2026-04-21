FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies (DB + CAD/PDF rendering fonts)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    netcat-traditional \
    fontconfig \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto-core \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
