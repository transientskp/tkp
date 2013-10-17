# Trap Celery Configuration

# This file uses the standard Celery configuration system.
# Please refer to the URL below for full documentation:
# http://docs.celeryproject.org/en/latest/configuration.html

# Uncomment the below for local use; that is, bypassing the task distribution
# system and running all tasks in serial in a single process. No broker or
# workers are required.
#CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Otherwise, configure the broker to which workers should connect and to which
# they will return results. This must be started independently of the
# pipeline.
BROKER_URL = CELERY_RESULT_BACKEND = 'amqp://guest@localhost//'

# This is used when you run a worker.
CELERY_IMPORTS = ("tkp.distribute.celery.tasks", )

# Don't reconfigure the logger, important for a worker.
CELERYD_HIJACK_ROOT_LOGGER = False
