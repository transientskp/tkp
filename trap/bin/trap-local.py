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
import trap.persistence
from lofarpipe.support.control import control
#from images_to_process import images

images = [
    '/home/gijs/Work/tkp-data/unittests/tkp_lib/quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits',
    '/home/gijs/Work/tkp-data/unittests/tkp_lib/quality/noise/good/home-pcarrol-msss-L086+69-analysis-band6.corr.fits',
]

class TrapImages(control):
    inputs = {}

    def pipeline_logic(self):
        quality_parset_file = self.task_definitions.get("quality_check", "parset")
        srcxtr_parset_file = self.task_definitions.get("source_extraction", "parset")

        self.logger.info("creating dataset in database ...")
        dataset_id = trap.persistence.store(images, 'trap-local dev run')
        self.logger.info("added dataset with ID %s" % dataset_id)

        dataset = DataSet(id=dataset_id, database=DataBase())
        dataset.update_images()

        good_images = []
        for image in dataset.images:
            if trap.quality.noise(image.id, quality_parset_file):
                    good_images.append(image)

        for image in good_images:
            trap.source_extraction.extract_sources(image.id, srcxtr_parset_file)

        for image in good_images:
            trap.monitoringlist.monitoringlist(image.id)

        #"transient_search", [dataset.id], image_ids=outputs['image_ids']
        #"feature_extraction", outputs['transients'])
        #"classification", outputs['transients'])
        #"prettyprint", outputs['transients'])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(TrapImages().main())