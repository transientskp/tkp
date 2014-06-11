"""
Importing this will initialise the Celery app and will try to load
a celeryconfig.py from you PYTHONPATH. The celery app can then be accessed
using tkp.distribute.celery.celery_app
"""
from __future__ import absolute_import
import warnings
import logging
from celery import Celery
from tkp.distribute.celery.log import monitor_events


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






