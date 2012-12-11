import logging
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

class MonetFilter(logging.Filter):
    def filter(self, record):
        return record.name != 'monetdb'


class TrapLocal(control):
    inputs = {}

    def pipeline_logic(self):
        logdrain = logging.getLogger()
        logdrain.level = self.logger.level
        logdrain.handlers = self.logger.handlers
        [h.addFilter(MonetFilter()) for h in logdrain.handlers]
        self.logger = logdrain

        quality_parset_file = self.task_definitions.get("quality_check", "parset")
        srcxtr_parset_file = self.task_definitions.get("source_extraction", "parset")
        transientsearch_file = self.task_definitions.get("transient_search", "parset")
        classification_file = self.task_definitions.get("classification", "parset")

        persistence_parset_file = self.task_definitions.get("persistence", "parset")
        dataset_id, image_ids = trap.ingredients.persistence.all(images, persistence_parset_file)

        good_image_ids = []
        for image_id in image_ids:
            if trap.ingredients.quality.check(image_id, quality_parset_file):
                good_image_ids.append(image_id)

        for image_id in good_image_ids:
            trap.ingredients.source_extraction.extract_sources(image_id, srcxtr_parset_file)

        # TODO: this should be updated to work on a list of images, not on a dataset ID
        trap.ingredients.monitoringlist.mark_sources(dataset_id, srcxtr_parset_file)

        for image_id in good_image_ids:
            trap.ingredients.monitoringlist.update_monitoringlist(image_id)

        transient_results = trap.ingredients.transient_search.search_transients(good_image_ids, dataset_id,  transientsearch_file)

        transients = transient_results['transients']
        for transient in transients:
            trap.ingredients.feature_extraction.extract_features(transient)
            trap.ingredients.classification.classify(transient, classification_file)