"""
This runs the TRAP locally (not using the lofar clustering mechanisms).
This is for development purposes only.
"""
import sys
import logging
from tkp.database import DataBase
from tkp.database import DataSet
import tkp.database as tkpdb
import trap.quality
import trap.source_extraction
import trap.monitoringlist
from lofarpipe.support.control import control
#from images_to_process import images

images = [
    '/home/gijs/Work/tkp-data/unittests/tkp_lib/quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits',
    '/home/gijs/Work/tkp-data/unittests/tkp_lib/quality/noise/good/home-pcarrol-msss-L086+69-analysis-band6.corr.fits',
]

class TrapImages(control):
    inputs = {}

    def pipeline_logic(self):
        database = DataBase()
        dataset = DataSet({'description': 'trap-local dev run'}, database)
        quality_parset_file = self.task_definitions.get("quality_check", "parset")
        srcxtr_parset_file = self.task_definitions.get("source_extraction", "parset")
        self.logger.info("Processing images ...")

        for image in images:
            self.logger.info("Processing image %s ..." % image)
            if not trap.quality.noise(image, dataset.id, quality_parset_file):
                continue

            trap.source_extraction.extract_sources(image, dataset.id, srcxtr_parset_file, False, "",  0, "")

        dataset.update_images()
        image_ids = [img.id for img in dataset.images]
        ids_filenames = tkpdb.utils.get_imagefiles_for_ids(database.connection, image_ids)

        for image_id, filename in ids_filenames:
            trap.monitoringlist.monitoringlist(filename, image_id, dataset.id)

        #"transient_search", [dataset.id], image_ids=outputs['image_ids']
        #"feature_extraction", outputs['transients'])
        #"classification", outputs['transients'])
        #"prettyprint", outputs['transients'])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(TrapImages().main())