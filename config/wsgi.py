"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from config.bootstrap import setup_django_settings

setup_django_settings()

application = get_wsgi_application()
