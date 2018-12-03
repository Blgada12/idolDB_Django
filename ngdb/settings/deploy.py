from .base import *

config_secret_deploy = json.loads(open(CONFIG_SECRET_DEPLOY_FILE).read())

DEBUG = False
ALLOWED_HOSTS = config_secret_deploy['django']['allowed_hosts']

WSGI_APPLICATION = 'ngdb.wsgi.deploy.application'

ROOT_URLCONF = 'ngdb.urls.deploy'

DATABASES = config_secret_common['django']['database'][0]