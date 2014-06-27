"""
All Celery worker tasks are defined here. No logic should be implemented here,
all functions should be a wrapper around the code in tkp.steps.
"""
from __future__ import absolute_import
import logging

from celery.utils.log import get_task_logger
from celery.signals import after_setup_logger
from celery.signals import after_setup_task_logger

from tkp.distribute.celery import celery_app
from tkp.distribute.celery.log import TaskLogEmitter
import tkp.steps


worker_logger = get_task_logger(__name__)


@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_task_log_emitter(sender=None, logger=None, loglevel=None,
                           logfile=None, format=None, colorize=None, **kwargs):
    """
    adds event emitter to every task logger and to every global logger.
    This should be run on the worker. Probably it is best do leave this
    function definition inside the task definition!
    """
    handler = TaskLogEmitter(celery_app)
    logger.addHandler(handler)


@celery_app.task
def persistence_node_step(images, image_cache_config):
    worker_logger.info("running persistence task")
    return tkp.steps.persistence.node_steps(images, image_cache_config)


@celery_app.task
def quality_reject_check(url, job_config):
    worker_logger.info("running quality task")
    return tkp.steps.quality.reject_check(url, job_config)


@celery_app.task
def extract_sources(url, extraction_params):
    worker_logger.info("running extracted sources task")
    return tkp.steps.source_extraction.extract_sources(url, extraction_params)


@celery_app.task
def test_log():
    """
    doesn't do much, only emit some log messages so we can test if the
    logging facilities are working
    """
    worker_logger.info("info from task")
    worker_logger.warning("warning from task")
    worker_logger.error("error from task")
    worker_logger.debug("debug from task")
