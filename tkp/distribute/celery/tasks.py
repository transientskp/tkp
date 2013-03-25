from celery import Celery
import tkp.steps.persistence

celery = Celery()

@celery.task
def extract_metadata(file):
    return tkp.steps.persistence.extract_metadatas([file])