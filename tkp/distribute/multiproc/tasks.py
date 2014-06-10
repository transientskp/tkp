"""
Parallisable tasks used with python multiprocessing
"""
from __future__ import absolute_import
import logging
import tkp.steps


logger = logging.getLogger(__name__)


def persistence_node_step(zipped):
    logger.info("running persistence task")
    images, args = zipped
    image_cache_config = args[0]
    return tkp.steps.persistence.node_steps(images, image_cache_config)


def quality_reject_check(zipped):
    logger.info("running quality task")
    url, args = zipped
    job_config = args[0]
    return tkp.steps.quality.reject_check(url, job_config)


def extract_sources(zipped):
    logger.info("running extracted sources task")
    url, args = zipped
    extraction_params = args[0]
    return tkp.steps.source_extraction.extract_sources(url, extraction_params)


def forced_fits(zipped):
    """
    :param detection_set: should be (url, detections) tuple
    :param extraction_params: null detections extraction_params
    :return:
    """
    logger.info("running forced fits task")
    detection_set, args = zipped
    url, detections = detection_set
    extraction_params = args[0]
    return tkp.steps.source_extraction.forced_fits(url, detections,
                                                   extraction_params)


def bogus(args):
    """
    doesn't do much, only emit some log messages so we can test if the
    logging facilities are working
    """
    logger.info('bogus called with %s' % str(args))
    logger.info("info from task")
    logger.warning("warning from task")
    logger.error("error from task")
    logger.debug("debug from task")
    return "love"