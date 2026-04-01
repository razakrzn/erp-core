ERP Core Deployment Guide
=========================

Recommended server
------------------

For this repo, the best balance of RAM, CPU performance, and cost is a single x86_64 VPS with:

- 4 dedicated vCPU
- 16 GB RAM
- 160 GB+ NVMe SSD

That size gives enough headroom for:

- Django + Gunicorn web process
- one Celery worker dedicated to cutting optimization
- PostgreSQL
- Redis
- Nginx
- DXF parsing + optimization bursts from apps/production/services/cutting_optimization.py

If your traffic is still low and cutting jobs are small, you can start with:

- 4 vCPU
- 8 GB RAM

Avoid going below 8 GB RAM if Postgres, Redis, web, and worker are all on the same machine.

Why this sizing fits cutting_optimization.py
--------------------------------------------

The cutting pipeline uses:

- ezdxf for CAD parsing
- shapely for geometry
- rectpack for nesting
- numpy for area calculations

These are not huge-memory libraries by themselves, but they create bursty CPU and RAM usage when:

- large CAD files are parsed
- many parts are flattened from splines/polylines
- multiple jobs run at once

For that reason, the production compose file pins Celery to:

- --concurrency=1
- --prefetch-multiplier=1

That keeps one cutting job from competing with another and protects the box from avoidable RAM spikes.

CAD format support note
-----------------------

This codebase is configured for DXF-only processing in production.

No external DWG converter is required, and `.dwg` uploads are rejected by API validation.

Cutting output note
-------------------

The cutting pipeline now stores optimization data only:

- extracted_parts
- optimization_result

No CAD PDF, cutlist PDF, or cutlist XLSX files are generated.

Production stack in this repo
-----------------------------

Use:

- docker-compose.prod.yml
- deploy/nginx.conf

Services included:

- nginx
- web
- celery
- db
- redis

Shared volumes:

- media_data for uploaded CAD files
- static_data for collected static files

Required environment variables
------------------------------

Set these in .env on the server:

DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=replace-me
DEBUG=False
ALLOWED_HOSTS=api.example.com
CORS_ALLOWED_ORIGINS=https://app.example.com
CSRF_TRUSTED_ORIGINS=https://api.example.com,https://app.example.com
DB_NAME=erp_core
DB_USER=erp_core
DB_PASSWORD=strong-password
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0

Notes:

- DB_HOST and DB_PORT are injected by docker-compose.prod.yml
- turn SECURE_SSL_REDIRECT=True on once TLS is terminating at the proxy/load balancer
- if you place the app behind Cloudflare, Caddy, or another TLS proxy, keep CSRF_TRUSTED_ORIGINS aligned with the public HTTPS origins

Deploy steps
------------

python manage.py migrate
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f celery

Schema cleanup migration note:

- Migration `production/0003_remove_cuttingoptimizationjob_cutlist_pdf_file_and_more.py` removes old cutlist file columns.
- Run migrations before (or during) first deployment on the updated code.

Suggested operating system
--------------------------

Use Ubuntu 24.04 LTS on x86_64 / AMD64 for the least friction with Python wheels and Docker images used by this repo.

When to split into multiple servers
-----------------------------------

Move to separate app and database servers when one of these becomes true:

- cutting jobs are frequent during business hours
- database size or query load starts competing with worker jobs
- you need stronger isolation for backups and maintenance
- you want zero-downtime deployments

The first split should be:

1. app server for nginx, web, celery, redis
2. managed PostgreSQL or separate Postgres VM

Platform note
-------------

This repo can run on Render, but the current architecture is a better fit for a VPS or VM because cutting jobs need:

- a separate worker
- Redis
- shared access to uploaded CAD media between web and worker

If you deploy on a platform where disks are attached to only one service, move media storage to S3-compatible object storage before using separate web and worker services.
