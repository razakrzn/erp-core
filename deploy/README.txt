ERP Core Deploy Media Safeguards
================================

Issue you saw
-------------

Media URL works, then after deploy the same URL returns 404.
This means the DB row is still present, but the physical file is gone from server disk.

Required persistent media path
------------------------------

- Django `MEDIA_ROOT` is hardcoded to: `/var/www/media`
- Nginx media alias should serve from: `/var/www/media`
- Container runtime must mount persistent volume to: `/var/www/media`

If `/var/www/media` is not persistent, files can disappear on redeploy.

Minimum checks (run on server)
------------------------------

1. Upload a test image in enquiry attachment.
2. Confirm the file exists:
   `ls -lah /var/www/media/crm/enquiries/`
3. Redeploy app.
4. Run the same `ls` command again.
5. Open the same media URL and confirm it still returns HTTP 200.

Docker/Coolify note
-------------------

Use a named/persistent volume mounted exactly at `/var/www/media`.
Do not mount media inside ephemeral app code paths.

Safe scripts
------------

- Backup media: `./deploy/scripts/backup_media.sh`
- Restore media: `./deploy/scripts/restore_media.sh <archive.tar.gz> --force`

Nginx reference config
----------------------

See `deploy/nginx.conf` and keep:

- `location /media/ { alias /var/www/media/; }`

