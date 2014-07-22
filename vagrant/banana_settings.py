from base import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INSTALLED_APPS += ['debug_toolbar']
DEBUG_TOOLBAR_PATCH_SETTINGS = False 

SECRET_KEY = "w;lkrjw3ljrd90A*W&#&Q@#(Q@EDMAE<fmsdlfjaowiepoq2ie"


DATABASES["vagrant"] = {
	'ENGINE': 'django.db.backends.postgresql_psycopg2',
	'HOST': 'localhost',
	'NAME': 'vagrant',
	'USER': 'vagrant',
	'PASSWORD': 'vagrant',
	'CONSOLE': False, 
}


ADMINS += [('Gijs Molenaar', 'webmaster@localhost'), ]

MONGODB = {
    "enabled": True,
    "host": "localhost",
    "port": 27017,
    "database": "tkp"
}

ALLOWED_HOSTS = [
    '127.0.0.1',
]
