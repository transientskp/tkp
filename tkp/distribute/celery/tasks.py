"""
All Celery worker tasks are defined here. No logic should be implemented here,
all functions should be a wrapper around the code in tkp.steps.
"""
import warnings
import logging
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
import tkp.steps


local_logger = logging.getLogger(__name__)
celery = Celery('tkp')
config_module = 'celeryconfig'


# try to load the celery config from the pipeline folder
try:
    celery.config_from_object(config_module)
except ImportError:
    msg = "can't find '%s' in your python path, using default config" % config_module
    warnings.warn(msg)
    local_logger.warn(msg)


class EventHandler(logging.Handler):
    """
    This log handler will emit talk-log events, which a client can listen to
    to rebroadcast the logging event.
    """
    def emit(self, record):
        with celery.events.default_dispatcher() as d:
            d.send('task-log', msg=record.getMessage(), levelno=record.levelno,
                   filename=record.filename)


@after_setup_logger.connect
@after_setup_task_logger.connect
def configure_logging(sender=None, logger=None, loglevel=None, logfile=None,
                      format=None, colorize=None, **kwargs):
    """ This adds event emitter to every task logger and to every global logger
    """
    handler = EventHandler()
    logger.addHandler(handler)
    #local_logger.addHandler(handler)


@celery.task
def persistence_node_step(images, p_parset):
    local_logger.info("running persistence task")
    return tkp.steps.persistence.node_steps(images, p_parset)


@celery.task
def quality_reject_check(url, job_config):
    local_logger.info("running quality task")
    return tkp.steps.quality.reject_check(url, job_config)


@celery.task
def extract_sources(url, se_parset):
    local_logger.info("running extracted sources task")
    return tkp.steps.source_extraction.extract_sources(url, se_parset)


@celery.task
def forced_fits(detection_set, parset):
    """
    :param detection_set: should be (url, detections) tuple
    :param parset: null detections parset
    :return:
    """
    local_logger.info("running forced fits task")
    url, detections = detection_set
    return tkp.steps.source_extraction.forced_fits(url, detections, parset)
