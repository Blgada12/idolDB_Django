from .base import *

config_secret_debug = json.loads(open(CONFIG_SECRET_DEBUG_FILE).read())

DEBUG = True
ALLOWED_HOSTS = config_secret_debug['django']['allowed_hosts']

WSGI_APPLICATION = 'ngdb.wsgi.debug.application'

ROOT_URLCONF = 'ngdb.urls.debug'

DATABASES = config_secret_common['django']['database'][0]