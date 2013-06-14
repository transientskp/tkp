# please refer to the url below for documentation:
# http://docs.celeryproject.org/en/latest/configuration.html

BROKER_URL = "redis://localhost:6379/0"
CELERY_IMPORTS = ("tkp.distribute.celery.tasks", )
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERYD_HIJACK_ROOT_LOGGER = False


# TODO: This is supposed to make celery run local, but I don't get it to work
# CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True