from celery import Celery
import tkp.steps

celery = Celery('tasks', backend='amqp', broker='amqp://guest@127.0.0.1:5672//')


@celery.task
def persistence_node_step(images, p_parset):
    return tkp.steps.persistence.node_step(images, p_parset)


@celery.task
def quality_reject_check(url, q_parset):
    return tkp.steps.quality.reject_check(url, q_parset)