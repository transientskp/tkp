import logging
import datetime
from lofarpipe.support.parset import parameterset
from trap import ingredients as ingred
import lofarpipe.support.lofaringredient as ingredient
from trap.ingredients.monitoringlist import add_manual_monitoringlist_entries
from tkp.database.orm import Image
from tkp.database.utils import general as dbgen
from tkp.database.utils import monitoringlist as dbmon
from tkp.database.utils import associations as dbass
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

        p_parset_file = self.task_definitions.get("persistence", "parset")
        q_parset_file = self.task_definitions.get("quality_check", "parset")
        se_parset_file = self.task_definitions.get("source_extraction", "parset")
        nd_parset_file = self.task_definitions.get("null_detections", "parset")
        mon_parset_file = self.task_definitions.get("mon_detections", "parset")
        ud_parset_file = self.task_definitions.get("user_detections", "parset")
        sa_parset_file = self.task_definitions.get("source_association", "parset")
        tr_parset_file = self.task_definitions.get("transient_search", "parset")
        cl_parset_file = self.task_definitions.get("classification", "parset")


        # persistence
        se_parset = ingred.source_extraction.parse_parset(se_parset_file)
        dataset_id, image_ids = ingred.persistence.all(images,
                                           se_parset['radius'], p_parset_file)

        # manual monitoringlist entries
        if not add_manual_monitoringlist_entries(dataset_id, self.inputs):
            return 1

        # quality_check
        good_image_ids = []
        for image_id in image_ids:
            image = Image(id=image_id)
            rejected = ingred.quality.reject_check(image.url, q_parset_file)
            if rejected:
                reason, comment = rejected
                ingred.quality.reject_image(image_id, reason, comment)
            else:
                good_image_ids.append(image_id)

        # Sourcefinding
        good_images = []
        transients = []
        for image_id in good_image_ids:
            image = Image(id=image_id)
            good_images.append(image)
            extracted_sources = ingred.source_extraction.extract_sources(
                                                     image.url, se_parset_file)
            dbgen.insert_extracted_sources(image_id, extracted_sources, 'blind')

            # null_detections
            nd_parset = parameterset(nd_parset_file)
            deRuiter_radius = nd_parset.getFloat('deRuiter_radius', 3.717)

            #for image in good_images:
            image_id = image.id
            image_path = image.url

            null_detections = dbmon.get_nulldetections(image_id, deRuiter_radius)
            ff_nd = ingred.source_extraction.forced_fits(image_path, null_detections)
            dbgen.insert_extracted_sources(image_id, ff_nd, 'ff_nd')

            # mon_detections - duplicates nulldetections
#            monsources = dbmon.get_monsources(image_id, deRuiter_radius)
#            ff_mon = ingred.source_extraction.forced_fits(image_path, monsources)
#            dbgen.insert_extracted_sources(image_id, ff_mon, 'ff_mon')

            ##User detections current unsupported.
            # user_detections

#            user_detections = dbmon.get_userdetections(image_id, deRuiter_radius)
#            ff_ud = ingred.source_extraction.forced_fits(image_path, user_detections)
#            dbgen.insert_extracted_sources(image_id, ff_ud, 'ff_ud')
#            dbgen.filter_userdetections_extracted_sources(image_id, deRuiter_radius)

            # Source_association
            dbass.associate_extracted_sources(image_id, deRuiter_r = deRuiter_radius)
            dbmon.add_nulldetections(image_id)

            # Transient_search
            transients = ingred.transient_search.search_transients(image_id, tr_parset_file)
            dbmon.adjust_transients_in_monitoringlist(image_id, transients)
        
        # Classification
        for transient in transients:
            ingred.feature_extraction.extract_features(transient)
            ingred.classification.classify(transient, cl_parset_file)
        
        now = datetime.datetime.utcnow()
        dbgen.update_dataset_process_ts(dataset_id, now)
