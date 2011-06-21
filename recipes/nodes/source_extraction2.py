#                                             LOFAR TRANSIENT DETECTION PIPELINE
#
#                                                         Source extraction node
#                                                                Evert Rol, 2011
#                                                          evert.astro@gmail.com
# ------------------------------------------------------------------------------

from __future__ import with_statement

import os
import sys
from contextlib import closing

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time

from tkp.config import config
from tkp.database.database import DataBase
from tkp.database.dataset import DataSet
from tkp.utility.accessors import FitsFile
from tkp.utility.accessors import dbimage_from_accessor
from tkp.utility.accessors import sourcefinder_image_from_accessor


class source_extraction(LOFARnodeTCP):
    """
    Extract sources from a FITS image
    """

    def run(self, image, detection_level=5, dataset_id=None,
            radius=1, dblogin={}):
        """

        Args:

            - image: FITS filename

        Kwargs:
        
            - detection_level: minimum detection level

            - dataset_id: dataset to which image belongs

            - dblogin: credentials for database connection/login

        """
        
        with log_time(self.logger):
            with closing(DataBase(**dblogin)) as database:
                description = 'LOFAR images'
                dataset = DataSet(name=description, dsid=dataset_id,
                                        database=database)
                self.logger.info("dataset id = %d" % dataset.dsid)
                self.outputs['dataset_id'] = dataset.dsid
                fitsimage = FitsFile(image)
                db_image = dbimage_from_accessor(dataset=dataset,
                                                 image=fitsimage)
                self.logger.info("Detecting sources in %s at %f level" % (
                    image, detection_level))
                data_image = sourcefinder_image_from_accessor(fitsimage)
                results = data_image.extract(det=detection_level)
                self.logger.info("Detected %d sources" % len(results))
                db_image.insert_extracted_sources(results)
                self.logger.info("saved extracted sources to database")
                db_image.associate_extracted_sources(
                    deRuiter_r=radius*
                    config['source_association']['deruiter_radius'])

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(source_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
