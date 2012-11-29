import sys
import logging
from tkp.database import DataBase, DataSet
import trap.ingredients.quality
import trap.ingredients.source_extraction
import trap.ingredients.monitoringlist
import trap.ingredients.persistence
import trap.ingredients.transient_search
import trap.ingredients.feature_extraction
import trap.ingredients.classification
import trap.ingredients.prettyprint
from lofarpipe.support.control import control

from images_to_process import images

import lofarpipe.support.lofaringredient as ingredient

class TrapLocal(control):
    inputs = {
        'dataset_id': ingredient.IntField(
            '--dataset-id',
            help='Specify a previous dataset id to append the results to.',
            default=-1
        ),
    }

    def pipeline_logic(self):
        logdrain = logging.getLogger()
        logdrain.level = self.logger.level
        logdrain.handlers += self.logger.handlers
        self.logger = logdrain

        quality_parset_file = self.task_definitions.get("quality_check", "parset")
        srcxtr_parset_file = self.task_definitions.get("source_extraction", "parset")
        transientsearch_file = self.task_definitions.get("transient_search", "parset")
        classification_file = self.task_definitions.get("classification", "parset")

        self.logger.info("creating dataset in database ...")
        dataset_id = trap.ingredients.persistence.store(images, 'trap-local dev run')
        self.logger.info("added dataset with ID %s" % dataset_id)

        dataset = DataSet(id=dataset_id, database=DataBase())
        dataset.update_images()

        good_images = []
        for image in dataset.images:
            if trap.ingredients.quality.check(image.id, quality_parset_file):
                good_images.append(image)

        for image in good_images:
            trap.ingredients.source_extraction.extract_sources(image.id, srcxtr_parset_file)

        # TODO: this should be updated to work on a list of images, not on a dataset ID
        trap.ingredients.monitoringlist.mark_sources(dataset_id, srcxtr_parset_file)

        for image in good_images:
            trap.ingredients.monitoringlist.update_monitoringlist(image.id)

        good_ids =[ i.id for i in good_images]
        transient_results = trap.ingredients.transient_search.search_transients(good_ids, dataset_id,  transientsearch_file)

        transients = transient_results['transients']
        for transient in transients:
            trap.ingredients.feature_extraction.extract_features(transient)
            trap.ingredients.classification.classify(transient, classification_file)