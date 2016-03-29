from __future__ import absolute_import
import logging
import tkp.steps


logger = logging.getLogger(__name__)


def persistence_node_step(images, image_cache_config, sigma, f):
    logger.debug("running persistence task")
    return tkp.steps.persistence.node_steps(images, image_cache_config,
                                            sigma, f)


def quality_reject_check(url, job_config):
    logger.debug("running quality task")
    return tkp.steps.quality.reject_check(url, job_config)


def extract_sources(url, extraction_params):
    logger.debug("running extracted sources task")
    return tkp.steps.source_extraction.extract_sources(url, extraction_params)
