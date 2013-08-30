"""
All Celery worker tasks are defined here. No logic should be implemented here,
all functions should be a wrapper around the code in tkp.steps.
"""
from __future__ import absolute_import
import logging
from tkp.distribute.celery.trap_app import trap
from tkp.distribute.common import deserialize
import tkp.steps


logger = logging.getLogger(__name__)


@trap.task
def persistence_node_step(images, p_parset, serialized=False):
    logger.info("running persistence task")
    if serialized:
        logger.info("deserializing payload")
        images = [deserialize(i) for i in images]
    return tkp.steps.persistence.node_steps(images, p_parset)


@trap.task
def quality_reject_check(url, job_config, serialized=False):
    logger.info("running quality task")
    if serialized:
        logger.info("deserializing payload")
        url = deserialize(url)
    return tkp.steps.quality.reject_check(url, job_config)


@trap.task
def extract_sources(url, se_parset, serialized=False):
    logger.info("running extracted sources task")
    if serialized:
        logger.info("deserializing payload")
        url = deserialize(url)
    return tkp.steps.source_extraction.extract_sources(url, se_parset)


@trap.task
def forced_fits(detection_set, parset, serialized=False):
    """
    :param detection_set: should be (url, detections) tuple
    :param parset: null detections parset
    :return:
    """
    logger.info("running forced fits task")
    url, detections = detection_set
    if serialized:
        logger.info("deserializing payload")
        url = deserialize(url)
    return tkp.steps.source_extraction.forced_fits(url, detections, parset)
