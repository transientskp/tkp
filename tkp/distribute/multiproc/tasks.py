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
    image_cache_config, sigma, f = args
    return tkp.steps.persistence.node_steps(images, image_cache_config,
                                            sigma, f)


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
