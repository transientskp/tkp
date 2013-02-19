import datetime
import logging
from lofarpipe.support.control import control
import lofarpipe.support.lofaringredient as ingredient
from trap.ingredients.monitoringlist import add_manual_monitoringlist_entries
from tkp.database import DataSet
from tkp.database.utils import general as dbgen
import trap.ingredients as ingred


class Trap(control):
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
        from images_to_process import images

        # capture all logging and sent it to the master
        logdrain = logging.getLogger()
        logdrain.level = self.logger.level
        logdrain.handlers = self.logger.handlers
        self.logger = logging.getLogger(__name__)


        if not images:
            self.logger.warn("No images found, check parameter files.")
            return 1

        se_parset_file = self.task_definitions.get("source_extraction", "parset")
        se_parset = ingred.source_extraction.parse_parset(se_parset_file)
        self.outputs.update(self.run_task(
            "persistence",
            images,
            extraction_radius_pix=se_parset['radius']
        ))

        dataset = DataSet(id=self.outputs['dataset_id'])
        dataset.update_images()

        if not add_manual_monitoringlist_entries(dataset.id, self.inputs):
            return 1

        # sets good_image_ids
        image_ids = [i.id for i in dataset.images]
        self.outputs.update(self.run_task(
            "quality_check",
            image_ids
        ))


        # sets sources_sets
        good_image_ids = self.outputs['good_image_ids']
        self.outputs.update(self.run_task(
            "source_extraction",
            good_image_ids,
        ))

        
        sources_sets = self.outputs['sources_sets']
        for (image_id, sources) in sources_sets:

            self.outputs.update(self.run_task(
                "insert_sources",
                [image_id, sources],
            ))

            self.outputs.update(self.run_task(
                "null_detections",
                [image_id],
            ))

            self.outputs.update(self.run_task(
                "mon_detections",
                [image_id],
            ))

            self.outputs.update(self.run_task(
                "user_detections",
                [image_id],
            ))

            self.outputs.update(self.run_task(
                "source_association",
                [image_id],
            ))

            self.outputs.update(self.run_task(
                "transient_search",
                [image_id],
            ))

        self.outputs.update(self.run_task(
            "feature_extraction",
            self.outputs['transients']
        ))

        self.outputs.update(self.run_task(
            "classification",
            self.outputs['transients']
        ))

        #self.run_task("prettyprint", self.outputs['transients'])

        now = datetime.datetime.utcnow()
        dbgen.update_dataset_process_ts(dataset.id, now)

    def _save_state(self):
        self.logger.info("skipping storing of pipeline state, since it doesn't work correctly at the moment")

