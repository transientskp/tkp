"""
All Celery worker tasks are defined here. No logic should be implemented here,
all functions should be a wrapper around the code in tkp.steps.
"""
from celery import Celery
import tkp.steps

celery = Celery('tkp')
celery.config_from_object('celeryconfig')

@celery.task
def persistence_node_step(images, p_parset):
    return tkp.steps.persistence.node_steps(images, p_parset)

@celery.task
def quality_reject_check(url, q_parset):
    return tkp.steps.quality.reject_check(url, q_parset)

@celery.task
def extract_sources(url, se_parset):
    return tkp.steps.source_extraction.extract_sources(url, se_parset)

@celery.task
def forced_fits(url, detections, parset):
    return tkp.steps.source_extraction.forced_fits(url, detections, parset)