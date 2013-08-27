from __future__ import absolute_import
import warnings
import logging
from celery import Celery
import tkp.steps


trap = Celery('trap')
config_module = 'celeryconfig'

local_logger = logging.getLogger(__name__)
# try to load the celery config from the pipeline folder
try:
    trap.config_from_object(config_module)
except ImportError:
    msg = "can't find '%s' in your python path, using default config" % config_module
    warnings.warn(msg)
    local_logger.warn(msg)


