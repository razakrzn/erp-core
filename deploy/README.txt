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

- docker-compose.yml
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

Set these in `.env` on the server (you can start from `.env.production.example`):

DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=replace-me
DEBUG=False
ALLOWED_HOSTS=api.example.com
CORS_ALLOWED_ORIGINS=https://app.example.com
CSRF_TRUSTED_ORIGINS=https://api.example.com,https://app.example.com
DB_NAME=erp_core
DB_USER=erp_core
DB_PASSWORD=strong-password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
CSRF_COOKIE_SAMESITE=Lax
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
USE_X_FORWARDED_HOST=True
SECURE_REFERRER_POLICY=strict-origin-when-cross-origin
X_FRAME_OPTIONS=DENY
SECURE_CROSS_ORIGIN_OPENER_POLICY=same-origin
LOG_LEVEL=INFO

Notes:

- DB_HOST and DB_PORT default to `db:5432` when omitted.
- if using a managed DB, set `DATABASE_URL` (optionally `DB_SSLMODE=require`) and it will override `DB_*`
- if your TLS terminates at a reverse proxy/load balancer, keep `SECURE_PROXY_SSL_HEADER` support and forward `X-Forwarded-Proto`
- if you place the app behind Cloudflare, Caddy, or another TLS proxy, keep CSRF_TRUSTED_ORIGINS aligned with the public HTTPS origins

Repository access for Docker deploy (SSH only)
----------------------------------------------

Use SSH-based Git access on the deployment host instead of HTTPS.

Initial server setup:

```bash
# 1) Generate a deploy key on the server (or reuse existing key)
ssh-keygen -t ed25519 -C "deploy@erp-core" -f ~/.ssh/id_ed25519 -N ""

# 2) Add ~/.ssh/id_ed25519.pub to GitHub (repo deploy key with read access)
# 3) Validate SSH auth
ssh -T git@github.com
```

Clone/update using SSH:

```bash
# Fresh clone
git clone git@github.com:razakrzn/erp-core.git

# If repo already exists and origin was HTTPS, switch it to SSH
git remote set-url origin git@github.com:razakrzn/erp-core.git
git pull origin main
```

Deploy steps
------------

python manage.py migrate
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml logs -f web
docker compose -f docker-compose.yml logs -f celery

Schema cleanup migration note:

- Migration `production/0003_remove_cuttingoptimizationjob_cutlist_pdf_file_and_more.py` removes old cutlist file columns.
- Run migrations before (or during) first deployment on the updated code.

Post-deploy verification
------------------------

Run these checks after deployment:

docker compose -f docker-compose.yml ps
curl -fsS http://127.0.0.1/healthz
docker compose -f docker-compose.yml logs --tail=100 web
docker compose -f docker-compose.yml logs --tail=100 celery
docker compose -f docker-compose.yml exec redis redis-cli ping
docker compose -f docker-compose.yml exec db pg_isready -U ${DB_USER} -d ${DB_NAME}

Expected:

- `/healthz` returns `ok`
- Redis returns `PONG`
- Postgres reports `accepting connections`
- no crash loop in `web` or `celery` logs

Cutting job smoke test:

- Create one cutting optimization job with a valid `.dxf` via API/admin.
- Confirm job status moves `pending` -> `processing` -> `completed`.
- Confirm `extracted_parts` and `optimization_result` are populated.
- Confirm no PDF/XLSX file output is expected.

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

Retention and backup policy (recommended)
-----------------------------------------

Storage targets:

- Keep VPS disk usage below 70% in normal operation.
- Alert at 70%, 85%, and 95%.
- Keep at least 30% free space for spikes and safe maintenance.

DXF/media retention:

- Keep all uploaded CAD files for 90 days by default.
- Keep files linked to active or recently updated jobs (last 180 days).
- Archive old files (older than 180 days) to object storage (S3-compatible).
- Delete local archived files after successful checksum verification in object storage.

Database backup policy (PostgreSQL):

- Daily logical backup (`pg_dump -Fc`) kept for 14 days.
- Weekly full backup kept for 8 weeks.
- Monthly backup kept for 12 months.
- Store backups off-server (object storage or separate backup server), not only on the VPS.

Redis policy:

- Redis is treated as cache/queue and is not a source of truth.
- Keep AOF enabled (already enabled in docker-compose.yml) for faster recovery.
- No long-term retention required for Redis data.

Docker/log retention:

- Rotate container logs (or limit log size with Docker logging options).
- Prune unused images weekly:
  `docker image prune -af --filter "until=168h"`
- Prune unused volumes only after confirming they are not used by running services.

Suggested backup schedule (cron examples):

- Daily at 02:00: `pg_dump -Fc` to local temp path, upload to object storage, remove local temp file.
- Weekly on Sunday 03:00: full compressed DB backup + integrity check + upload.
- Monthly on day 1 at 04:00: monthly snapshot/backup copy tagged with year-month.

Backup and restore scripts (included)
-------------------------------------

Scripts are available in `deploy/scripts/`:

- `backup_db.sh`
- `backup_media.sh`
- `backup_all.sh`
- `restore_db.sh`
- `restore_media.sh`

Usage:

- DB backup:
  `./deploy/scripts/backup_db.sh`
- Media backup:
  `./deploy/scripts/backup_media.sh`
- Run both:
  `./deploy/scripts/backup_all.sh`
- Restore DB (destructive; requires explicit confirmation):
  `FORCE_RESTORE=YES ./deploy/scripts/restore_db.sh deploy/backups/db/<file>.dump`
- Restore media (destructive; requires explicit confirmation):
  `FORCE_RESTORE=YES ./deploy/scripts/restore_media.sh deploy/backups/media/<file>.tar.gz`

Script behavior:

- Scripts read `.env` and `docker-compose.yml` by default.
- Optional overrides:
  - `COMPOSE_FILE=/path/to/docker-compose.yml`
  - `ENV_FILE=/path/to/.env`
  - `BACKUP_DIR=/custom/backup/path`
  - `RETENTION_DAYS=14` (DB default) / `RETENTION_DAYS=30` (media default)
- DB restore stops `web` and `celery`, restores DB, runs migrations, then starts services.
- Media restore stops `web` and `celery`, replaces media content, then starts services.

Recovery test policy:

- Run a restore drill at least once per month:
  1. restore latest backup to a staging database
  2. run Django migrations/checks
  3. verify API login and one cutting job read path
- Keep a short runbook of restore steps and recovery times.

Operational rules for this repo:

- Since cutting outputs are JSON-only now, do not allocate retention for generated PDF/XLSX artifacts.
- Retention focus should be:
  1. PostgreSQL data
  2. uploaded DXF files (`media_data`)
  3. deployment artifacts and logs

Managed DB migration runbook (no data loss)
-------------------------------------------

Goal:

- Start with PostgreSQL on VPS now.
- Migrate to managed PostgreSQL later with safe cutover and no data loss.

Pre-checks (before cutover day):

- Ensure managed DB PostgreSQL major version is same or newer than VPS DB.
- Confirm network access from VPS to managed DB host/port.
- Keep credentials ready:
  - `SRC_DB_*` for current VPS DB
  - `DST_DB_*` for managed DB

On VPS, check versions:

`docker compose -f docker-compose.yml exec db psql -U ${DB_USER} -d ${DB_NAME} -c "select version();"`

Migration steps (recommended):

1. Create an initial test dump and restore to managed DB (dry run).
2. Validate app against managed DB in a staging environment.
3. Schedule a short maintenance window for final cutover.
4. Stop write traffic and background workers.
5. Take final dump from VPS DB.
6. Restore final dump to managed DB.
7. Point app to managed `DATABASE_URL`.
8. Run migrations and start services.
9. Verify app flows.
10. Keep old VPS DB read-only for 24-72 hours as rollback safety.

Cutover commands (copy/paste template):

```bash
# 0) Variables (edit values)
export SRC_DB_NAME="erp_core"
export SRC_DB_USER="erp_core"
export SRC_DB_PASSWORD="old-password"
export SRC_DB_HOST="127.0.0.1"
export SRC_DB_PORT="5432"

export DST_DB_NAME="erp_core"
export DST_DB_USER="managed_user"
export DST_DB_PASSWORD="managed_password"
export DST_DB_HOST="managed-db-host"
export DST_DB_PORT="5432"
export DUMP_FILE="/tmp/erp_core_cutover.dump"

# 1) Stop app writes (maintenance window)
docker compose -f docker-compose.yml stop web celery

# 2) Final backup from source VPS DB
PGPASSWORD="$SRC_DB_PASSWORD" pg_dump \
  -h "$SRC_DB_HOST" -p "$SRC_DB_PORT" \
  -U "$SRC_DB_USER" -d "$SRC_DB_NAME" \
  -Fc -f "$DUMP_FILE"

# 3) Restore into managed DB
PGPASSWORD="$DST_DB_PASSWORD" pg_restore \
  -h "$DST_DB_HOST" -p "$DST_DB_PORT" \
  -U "$DST_DB_USER" -d "$DST_DB_NAME" \
  --clean --if-exists --no-owner --no-privileges \
  "$DUMP_FILE"

# 4) Update DATABASE_URL in .env to managed DB
# Example:
# DATABASE_URL=postgresql://managed_user:managed_password@managed-db-host:5432/erp_core

# 5) Apply migrations using the new DB
docker compose -f docker-compose.yml run --rm web python manage.py migrate

# 6) Start app again
docker compose -f docker-compose.yml up -d web celery nginx redis

# 7) Verify health
curl -fsS http://127.0.0.1/healthz
docker compose -f docker-compose.yml logs --tail=100 web
docker compose -f docker-compose.yml logs --tail=100 celery
```

Post-cutover verification:

- Login works.
- API read/write works.
- One cutting job completes (`pending` -> `processing` -> `completed`).
- Critical table counts match (sample checks):
  - users
  - production jobs
  - inventory records

Rollback plan:

- If verification fails, stop web/celery, restore old `DATABASE_URL` in `.env`, and start services again.
- Keep old VPS DB unchanged during rollback window.

Phased DB strategy: KVM local DB -> Neon later
----------------------------------------------

Yes, this project can safely start with PostgreSQL on VPS local storage and migrate to Neon later.

Phase 1 (initial, lower cost):

- Run PostgreSQL in `docker-compose.yml` using local volume `postgres_data`.
- Keep Redis, web, celery, and nginx on the same VPS.
- Apply strict backup policy from day 1:
  - daily DB dumps off-server
  - weekly restore test on staging
- Keep disk usage below 70% and reserve at least 30% free space.

Phase 2 (scale/reliability upgrade):

- Move DB to Neon when one or more of these is true:
  - DB growth is accelerating
  - backup/restore operations are taking too long
  - you want managed failover and easier operations
  - app downtime risk from single-server DB becomes unacceptable

Cutover summary (local DB -> Neon):

1. Schedule maintenance window.
2. Stop write traffic (`web` + `celery`).
3. Take final `pg_dump -Fc` from local DB.
4. Restore into Neon.
5. Update `DATABASE_URL` in `.env` to Neon connection string.
6. Run Django migrations.
7. Start services and verify app flows.
8. Keep old local DB untouched for 24-72 hours as rollback safety.

No data loss notes:

- Use same/newer PostgreSQL major version on Neon.
- Stop background workers during final cutover.
- Verify critical table counts and one full business flow before ending maintenance.

Decision checklist: stay local DB vs move to Neon
-------------------------------------------------

Use this quick checklist during planning reviews:

Stay on local KVM PostgreSQL if:

- DB size is still small (for example under 20-30 GB).
- Team is comfortable handling backups/restores and DB maintenance.
- Restore drills are passing and recovery time is acceptable.
- Single-server DB downtime risk is currently acceptable.
- Cost minimization is top priority right now.

Move to Neon if:

- DB size is growing quickly month over month.
- Backup windows and restore times are getting too long.
- Team wants managed operations and reduced DB maintenance burden.
- You need stronger reliability posture without managing DB failover yourself.
- Any customer-facing downtime from DB issues is becoming unacceptable.

Rule of thumb:

- If two or more "Move to Neon" points are true, plan migration in the next sprint.
- If backup or restore confidence is low, prioritize migration immediately.
