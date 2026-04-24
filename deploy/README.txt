ERP Core Deployment Guide
=========================

Hardcoded Setup
---------------

This project now uses hardcoded runtime configuration only.

Application Defaults
--------------------

- Django settings module: `config.settings`
- Database engine: MySQL
- Database name: `emrdb`
- Database user: `root`
- Database host: `72.62.254.95`
- Database port: `3307`
- Media root: `<repo>/media`

Run (Local)
-----------

1. Install dependencies:
   `pip install -r requirements.txt`
2. Run migrations:
   `python manage.py migrate`
3. Start server:
   `python manage.py runserver`

Docker Notes
------------

- `Dockerfile` builds and runs the app with hardcoded Django settings.
- `render.yaml` keeps only service type/runtime/name and does not define env vars.

Backup/Restore Scripts
----------------------

- DB backup script uses hardcoded values inside script:
  - `deploy/scripts/backup_db.sh`
- DB restore script requires explicit force flag:
  - `deploy/scripts/restore_db.sh <backup.dump> --force`
- Media restore script requires explicit force flag:
  - `deploy/scripts/restore_media.sh <media.tar.gz> --force`

Safety
------

Restore scripts stop web/celery before restore and start them after restore.
Use `--force` only when you are sure about replacing current data.
