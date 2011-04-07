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

from tkp.settings import DERUITER_R
from tkp.sourcefinder.accessors import FitsFile
from tkp.sourcefinder.image import ImageData
from tkp.database.dataset import DataSet
import tkp.database.database as tkpdb
from tkp.database.utils import insertExtractedSources
from tkp.database.utils import associateExtractedSources
            

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
            with closing(tkpdb.connection(**dblogin)) as dbconnection:
                description = 'LOFAR images'
                dataset = DataSet(description, dbconnection=dbconnection, id=dataset_id)
                self.logger.info("dataset id = %d" % dataset.id)
                self.outputs['dataset_id'] = dataset.id
                image_data = ImageData(FitsFile(image), conn=dbconnection, dataset=dataset)
                self.logger.info("Detecting sources in %s at %f level" % (
                    image, detection_level))
                results = image_data.sextract(det=detection_level)
                self.logger.info("Detected %d sources" % len(results))
                insertExtractedSources(dbconnection, image_data.id[0], results)#,
#                                       logger=self.logger)
                #tkpdb.savetoDB(dataset=dataset, objectlist=results,
                #               conn=dbconnection)
                self.logger.info("saved extracted sources to database")
                associateExtractedSources(dbconnection, image_data.id[0],
                                          deRuiter_r=radius*DERUITER_R,
                                          logger=self.logger)
    

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(source_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
