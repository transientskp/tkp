from __future__ import absolute_import
import logging
import tkp.steps


logger = logging.getLogger(__name__)


def save_to_mongodb(images, image_cache_config):
    logger.debug("running persistence task")
    return tkp.steps.persistence.save_to_mongodb(images, image_cache_config)


def extract_metadatas(accessors, sigma, f):
    logger.info("running extract metadatas task")
    return tkp.steps.persistence.extract_metadatas(accessors, sigma, f)


def quality_reject_check(accessor, job_config):
    logger.debug("running quality task")
    return tkp.steps.quality.reject_check(accessor, job_config)


def extract_sources(accessor, extraction_params):
    logger.debug("running extracted sources task")
    return tkp.steps.source_extraction.extract_sources(accessor,
                                                       extraction_params)


def get_accessors(images):
    logger.debug("Creating accessors for images")
    return tkp.steps.persistence.get_accessors(images)
