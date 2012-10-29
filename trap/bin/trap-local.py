"""
This runs the TRAP locally (not using the lofar clustering/recipes code).
This is for development purposes only.
"""

from tkp.database import DataBase
from tkp.database import DataSet
import trap.quality
import logging
from images_to_process import images

logging.basicConfig(level=logging.INFO)

quality_parset_file = '/home/gijs/pipeline-runtime/jobs/devel/parsets/quality_check.parset'

database = DataBase()
dataset = DataSet({'description': 'trap-local dev run'}, database)

logging.info("Processing images ...")
good_images = []
for ctr, image in enumerate(images):
    logging.info("Processing image %s ..." % image)
    # quality check
    if not trap.quality.noise(image, dataset.id, quality_parset_file):
        continue

