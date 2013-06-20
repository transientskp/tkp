"""
All Celery worker tasks are defined here. No logic should be implemented here,
all functions should be a wrapper around the code in tkp.steps.

convention here is func(iter, *arguments). So the iter element as first
argument
"""
import warnings
import logging

from celery import Celery

import tkp.steps


logger = logging.getLogger(__name__)

celery = Celery('tkp')
config_module = 'celeryconfig'

try:
    celery.config_from_object(config_module)
except ImportError:
    msg = "can't find '%s' in your python path, using default config" % config_module
    warnings.warn(msg)
    logger.warn(msg)

@celery.task
def persistence_node_step(images, p_parset):
    return tkp.steps.persistence.node_steps(images, p_parset)

@celery.task
def quality_reject_check(url, job_config):
    return tkp.steps.quality.reject_check(url, job_config)

@celery.task
def extract_sources(url, se_parset):
    return tkp.steps.source_extraction.extract_sources(url, se_parset)

@celery.task
def forced_fits(detection_set, parset):
    """

    :param detection_set: should be (url, detections) tuple
    :param parset: null detections parset
    :return:
    """
    url, detections = detection_set
    return tkp.steps.source_extraction.forced_fits(url, detections, parset)
