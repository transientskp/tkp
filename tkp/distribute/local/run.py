import logging
import datetime
import os
import imp
import lofarpipe.support.lofaringredient as ingredient
from tkp.steps.monitoringlist import add_manual_monitoringlist_entries
from tkp import steps
from tkp.db.orm import Image
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db import associations as dbass
from lofarpipe.support.control import control
from tkp.distribute.common import load_job_config, dump_job_config_to_logdir
import tkp.utility.parset as parset


class MonetFilter(logging.Filter):
    def filter(self, record):
        return record.name != 'monetdb'


class TrapLocal(control):
    inputs = {
        'monitor_coords': ingredient.StringField(
            '-m', '--monitor-coords',
            optional=True
        ),
        'monitor_list': ingredient.FileField(
            '-l', '--monitor-list',
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
        logdrain = logging.getLogger()
        logdrain.level = self.logger.level
        logdrain.handlers = self.logger.handlers
        [h.addFilter(MonetFilter()) for h in logdrain.handlers]
        self.logger = logdrain

        job_config = load_job_config(self.task_definitions)
        dump_job_config_to_logdir(self.config, job_config)
        job_dir = self.config.get('layout', 'job_directory')
        images = imp.load_source('images_to_process', os.path.join(job_dir,
                                 'images_to_process.py')).images


        p_parset = parset.load_section(job_config, 'persistence')
        q_lofar_parset = parset.load_section(job_config, 'quality_lofar')
        se_parset = parset.load_section(job_config, 'source_extraction')
        nd_parset = parset.load_section(job_config, 'null_detections')
        tr_parset = parset.load_section(job_config, 'transient_search')


        # persistence
        metadatas = steps.persistence.node_steps(images, p_parset)
        dataset_id, image_ids = steps.persistence.master_steps(metadatas,
                                                               se_parset['radius'],
                                                               p_parset)

        # manual monitoringlist entries
        if not add_manual_monitoringlist_entries(dataset_id, self.inputs):
            return 1

        # quality_check
        good_image_ids = []
        for image_id in image_ids:
            image = Image(id=image_id)
            rejected = steps.quality.reject_check(image.url, q_lofar_parset)
            if rejected:
                reason, comment = rejected
                steps.quality.reject_image(image_id, reason, comment)
            else:
                good_image_ids.append(image_id)

        # Sourcefinding
        good_images = []
        transients = []
        for image_id in good_image_ids:
            image = Image(id=image_id)
            good_images.append(image)
            extracted_sources = steps.source_extraction.extract_sources(
                                                     image.url, se_parset)
            dbgen.insert_extracted_sources(image_id, extracted_sources,
                                           'blind')

            # null_detections
            deRuiter_radius = nd_parset['deruiter_radius']

            #for image in good_images:
            image_id = image.id
            image_path = image.url

            null_detections = dbmon.get_nulldetections(image_id,
                                                       deRuiter_radius)
            ff_nd = steps.source_extraction.forced_fits(image_path,
                                                        null_detections,
                                                        nd_parset)
            dbgen.insert_extracted_sources(image_id, ff_nd, 'ff_nd')

            # Source_association
            dbass.associate_extracted_sources(image_id,
                                              deRuiter_r=deRuiter_radius)
            dbmon.add_nulldetections(image_id)

            # Transient_search
            transients = steps.transient_search.search_transients(image_id,
                                                                  tr_parset)
            dbmon.adjust_transients_in_monitoringlist(image_id, transients)

        # Classification
        for transient in transients:
            steps.feature_extraction.extract_features(transient)
#            ingred.classification.classify(transient, cl_parset)

        now = datetime.datetime.utcnow()
        dbgen.update_dataset_process_ts(dataset_id, now)
