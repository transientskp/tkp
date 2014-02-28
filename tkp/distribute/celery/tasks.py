from __future__ import absolute_import
"""
All Celery worker tasks are defined here. No logic should be implemented here,
all functions should be a wrapper around the code in tkp.steps.
"""
import warnings
import logging
from tkp.distribute.celery.trap_app import trap
import tkp.steps

local_logger = logging.getLogger(__name__)


@trap.task
def persistence_node_step(images, image_cache_config):
    local_logger.info("running persistence task")
    return tkp.steps.persistence.node_steps(images, image_cache_config)


@trap.task
def quality_reject_check(url, job_config):
    local_logger.info("running quality task")
    return tkp.steps.quality.reject_check(url, job_config)


@trap.task
def extract_sources(url, extraction_params):
    local_logger.info("running extracted sources task")
    return tkp.steps.source_extraction.extract_sources(url, extraction_params)


@trap.task
def forced_fits(detection_set, extraction_params):
    """
    :param detection_set: should be (url, detections) tuple
    :param extraction_params: null detections extraction_params
    :return:
    """
    local_logger.info("running forced fits task")
    url, detections = detection_set
    return tkp.steps.source_extraction.forced_fits(url, detections, extraction_params)
