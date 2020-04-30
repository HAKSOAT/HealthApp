"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from dotenv import load_dotenv
import django
from channels.routing import get_default_application

load_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['ASGI_THREADS'] = "4"
django.setup()

application = get_default_application()
