from celery import Celery
import tkp.steps

#celery = Celery('tasks', backend='amqp', broker='amqp://guest@127.0.0.1:5672//')
celery = Celery('tasks', backend='redis', broker='redis://localhost:6379/0')



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