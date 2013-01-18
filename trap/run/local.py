import logging
from trap import ingredients as ingred
import lofarpipe.support.lofaringredient as ingredient
from trap.ingredients.monitoringlist import add_manual_monitoringlist_entries
from lofarpipe.support.control import control

from images_to_process import images

class MonetFilter(logging.Filter):
    def filter(self, record):
        return record.name != 'monetdb'


class TrapLocal(control):
    inputs = {
        'monitor_coords': ingredient.StringField(
            '-m', '--monitor-coords',
            # Unfortunately the ingredient system cannot handle spaces in
            # parameter fields. I have tried enclosing with quotes, switching
            # to StringField, still no good.
            help='Specify a list of RA,DEC co-ordinate pairs to monitor\n'
                 '(decimal degrees, no spaces), e.g.:\n'
                 '--monitor-coords=[[137.01,14.02],[137.05,15.01]]',
            optional=True
        ),
        'monitor_list': ingredient.FileField(
            '-l', '--monitor-list',
            help='Specify a file containing a list of RA,DEC'
                 'co-ordinates to monitor, e.g.\n'
                 '--monitor-list=my_coords.txt\n'
                 'File should contain a list of RA,DEC pairs (each in list form), e.g.\n'
                 '[ [137.01,14.02], [137.05,15.01]] \n'
            ,
            optional=True
        ),
        }

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
        dataset_id, image_ids = ingred.persistence.all(images, persistence_parset_file)

        add_manual_monitoringlist_entries(dataset_id, self.inputs)

        good_image_ids = []
        for image_id in image_ids:
            if ingred.quality.check(image_id, quality_parset_file):
                good_image_ids.append(image_id)

        for image_id in good_image_ids:
            ingred.source_extraction.extract_sources(image_id,
                                                       srcxtr_parset_file)

        # TODO: this should be updated to work on a list of images, not on a dataset ID
        ingred.monitoringlist.mark_sources(dataset_id, srcxtr_parset_file)

        for image_id in good_image_ids:
            ingred.monitoringlist.update_monitoringlist(image_id)

        transient_results = ingred.transient_search.search_transients(
                              good_image_ids, dataset_id, transientsearch_file)

        transients = transient_results['transients']
        for transient in transients:
            ingred.feature_extraction.extract_features(transient)
            ingred.classification.classify(transient, classification_file)

