from __future__ import with_statement
import datetime
import logging
from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
import lofarpipe.support.lofaringredient as ingredient
from trap.ingredients.monitoringlist import add_manual_monitoringlist_entries
from tkp.database import DataBase
from tkp.database import DataSet


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

        logdrain = logging.getLogger()
        logdrain.level = self.logger.level
        logdrain.handlers = self.logger.handlers
        self.logger = logdrain

        log_time(self.logger)
        if not images:
            self.logger.warn("No images found, check parameter files.")
            return 1

        self.logger.info("creating dataset in database ...")
        self.outputs.update(self.run_task(
            "persistence",
            images,
        ))

        dataset = DataSet(id=self.outputs['dataset_id'], database=DataBase())
        dataset.update_images()

        add_manual_monitoringlist_entries(dataset.id, self.inputs)

        self.outputs.update(self.run_task(
            "quality_check",
            [i.id for i in dataset.images],
            nproc=1 # Issue #3357
        ))

        self.outputs.update(self.run_task(
            "source_extraction",
            self.outputs['good_image_ids'],
            #nproc = self.config.get('DEFAULT', 'default_nproc')
            nproc=1 # Issue #3357
        ))

        self.outputs.update(self.run_task(
            "monitoringlist", [dataset.id],
            nproc=1 # Issue #3357
        ))

        self.outputs.update(self.run_task(
            "transient_search", [dataset.id],
            image_ids=self.outputs['good_image_ids']
        ))

        self.outputs.update(self.run_task(
            "feature_extraction",
            self.outputs['transients']
        ))

        self.outputs.update(self.run_task(
            "classification",
            self.outputs['transients']
        ))

        self.run_task("prettyprint", self.outputs['transients'])

        dataset.process_ts = datetime.datetime.utcnow()
