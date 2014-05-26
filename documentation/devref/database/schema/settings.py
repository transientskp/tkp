SECRET_KEY = 'bla'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gijs',
        'USER': 'gijs',
        'PASSWORD': 'gijs',
    }
}


INSTALLED_APPS = (
    'django_extensions',
    'app',
)
