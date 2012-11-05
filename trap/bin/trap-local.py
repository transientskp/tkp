"""
This runs the TRAP locally (not using the lofar clustering mechanisms).
This is for development purposes only.
"""
import sys
import logging
from tkp.database import DataBase, DataSet
import trap.quality
import trap.source_extraction
import trap.monitoringlist
import trap.persistence
import trap.transient_search
import trap.feature_extraction
import trap.classification
import trap.prettyprint
from lofarpipe.support.control import control

from images_to_process import images


class TrapImages(control):
    inputs = {}

    def pipeline_logic(self):
        quality_parset_file = self.task_definitions.get("quality_check", "parset")
        srcxtr_parset_file = self.task_definitions.get("source_extraction", "parset")
        transientsearch_file = self.task_definitions.get("transient_search", "parset")
        classification_file = self.task_definitions.get("classification", "parset")

        self.logger.info("creating dataset in database ...")
        dataset_id = trap.persistence.store(images, 'trap-local dev run')
        self.logger.info("added dataset with ID %s" % dataset_id)

        dataset = DataSet(id=dataset_id, database=DataBase())
        dataset.update_images()

        for image in dataset.images:
            if not trap.quality.noise(image.id, quality_parset_file):
                # don't process rejected files any further
                continue

            trap.source_extraction.extract_sources(image.id, srcxtr_parset_file)
            trap.monitoringlist.mark_sources(dataset_id, srcxtr_parset_file)
            trap.monitoringlist.update_monitoringlist(image.id)
            transient_results = trap.transient_search.search_transients([image.id], dataset_id, transientsearch_file)
            transients = transient_results['transients']
            for transient in transients:
                trap.feature_extraction.extract_features(transient)
                trap.classification.classify(transient, classification_file)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(TrapImages().main())