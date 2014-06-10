from __future__ import absolute_import
import logging
import tkp.steps


logger = logging.getLogger(__name__)


def persistence_node_step(images, image_cache_config):
    logger.info("running persistence task")
    return tkp.steps.persistence.node_steps(images, image_cache_config)


def quality_reject_check(url, job_config):
    logger.info("running quality task")
    return tkp.steps.quality.reject_check(url, job_config)


def extract_sources(url, extraction_params):
    logger.info("running extracted sources task")
    return tkp.steps.source_extraction.extract_sources(url, extraction_params)


def forced_fits(detection_set, extraction_params):
    """
    :param detection_set: should be (url, detections) tuple
    :param extraction_params: null detections extraction_params
    :return:
    """
    logger.info("running forced fits task")
    url, detections = detection_set
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