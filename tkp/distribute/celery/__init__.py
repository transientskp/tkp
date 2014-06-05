"""
Importing this will initialise the Celery app and will try to load
a celeryconfig.py from you PYTHONPATH. The celery app can then be accessed
using tkp.distribute.celery.celery_app
"""
from __future__ import absolute_import
import warnings
import logging
from celery import Celery, group
from tkp.distribute.celery.log import monitor_events, setup_event_listening

local_logger = logging.getLogger(__name__)
config_module = 'celeryconfig'

celery_app = Celery('trap')
# try to load the celery config from the pipeline folder
try:
    celery_app.config_from_object(config_module)
    celery_app.connection()
except ImportError:
    msg = "can't find '%s' in your python path, using default config" % \
          config_module
    warnings.warn(msg)
    local_logger.warn(msg)
    celery_app.config_from_object({})


setup_event_listening(celery_app)


def map(func, iterable, arguments=[]):
    if iterable:
        return group(func.s(i, *arguments) for i in iterable)().get()
    else:
        # group()() returns None if group is called with no arguments,
        # leading to an AttributeError with get().
        return []

def set_cores(cores=0):
    """
    doesn't do anything for celery
    """
    pass
