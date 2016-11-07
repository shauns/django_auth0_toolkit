DEBUG = True

SECRET_KEY = 'shhh'

ROOT_URLCONF = 'test_project.urls'

AUTH0_DOMAIN = 'testing.auth0.com'

AUTH0_CLIENT_ID = 'client-id-from-auth0'

AUTH0_CLIENT_SECRET = 'client-secret-from-auth0'

AUTH0_LOGIN_CALLBACK_URL = '/handle-auth0-callback'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
]
