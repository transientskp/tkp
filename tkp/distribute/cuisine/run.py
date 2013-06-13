import datetime
import logging
import os
import imp
from lofarpipe.support.control import control
import lofarpipe.support.lofaringredient as ingredient
from tkp.steps.monitoringlist import add_manual_monitoringlist_entries
from tkp.db import DataSet
from tkp.db import general as dbgen
from tkp import steps
from tkp.distribute.common import load_job_config
import tkp.utility.parset as parset


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
        # we need to add the TKP flags here also, otherwise LOFAR pipeline
        # will barf
        'distribute': ingredient.StringField(
            '-f', '--method',
            optional=True
        )
    }

    def pipeline_logic(self):

        job_dir = self.config.get('layout', 'job_directory')
        images = imp.load_source('images_to_process', os.path.join(job_dir,
                                 'images_to_process.py')).images

        # capture all logging and sent it to the master
        logdrain = logging.getLogger()
        logdrain.level = self.logger.level
        logdrain.handlers = self.logger.handlers
        self.logger = logging.getLogger(__name__)


        if not images:
            self.logger.warn("No images found, check parameter files.")
            return 1

        job_config = load_job_config(self.task_definitions)
        p_parset = parset.load_section(job_config, 'persistence')
        q_lofar_parset = parset.load_section(job_config, 'quality_lofar')
        se_parset = parset.load_section(job_config, 'source_extraction')
        nd_parset = parset.load_section(job_config, 'null_detections')
        tr_parset = parset.load_section(job_config, 'transient_search')
        assoc_parset = parset.load_section(job_config, 'association')

        self.outputs.update(self.run_task(
            "persistence",
            images,
            parset=p_parset,
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
            image_ids,
            parset=q_lofar_parset
        ))


        # sets sources_sets
        good_image_ids = self.outputs['good_image_ids']
        self.outputs.update(self.run_task(
            "source_extraction",
            good_image_ids,
            parset=se_parset
        ))


        sources_sets = self.outputs['sources_sets']
        for (image_id, sources) in sources_sets:

            self.outputs.update(self.run_task(
                "insert_sources",
                [image_id, sources],
            ))

        self.outputs.update(self.run_task(
            "null_detections",
            good_image_ids,
            parset=nd_parset
        ))

        for (image_id, sources) in sources_sets:
            self.outputs.update(self.run_task(
                "source_association",
                [image_id],
                parset=assoc_parset
            ))

            self.outputs.update(self.run_task(
                "transient_search",
                [image_id],
                parset=tr_parset
            ))

        self.outputs.update(self.run_task(
            "feature_extraction",
            self.outputs['transients']
        ))

        now = datetime.datetime.utcnow()
        dbgen.update_dataset_process_ts(dataset.id, now)

    def _save_state(self):
        self.logger.info("skipping storing of pipeline state, since it doesn't work correctly at the moment")

