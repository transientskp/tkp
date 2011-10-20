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


class source_extraction(LOFARnodeTCP):
    """
    Extract sources from a FITS image
    """

    def run(self, image, detection_level=5,
            dataset_id=None, radius=1, tkpconfigdir=None):
        if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
            os.environ['TKPCONFIGDIR'] = tkpconfigdir
        import tkp
        from tkp.config import config
        from tkp.database.database import DataBase
        from tkp.database.database import ENGINE
        from tkp.database.dataset import DataSet
        from tkp.utility.accessors import FITSImage
        from tkp.utility.accessors import dbimage_from_accessor
        from tkp.utility.accessors import sourcefinder_image_from_accessor
        """

        Args:

            - image: FITS filename

        Kwargs:
        
            - detection_level: minimum detection level

            - dataset_id: dataset to which image belongs

            - source association radius, in multiples of the De Ruiter
              radius; the latter is defined in the TKP configuration
              file.

        """
        
        with log_time(self.logger):
            with closing(DataBase()) as database:
                self.logger.info("ENGINE = %s", ENGINE)
                dataset = DataSet(id=dataset_id, database=database)
                fitsimage = FITSImage(image)
                db_image = dbimage_from_accessor(dataset=dataset,
                                                 image=fitsimage)
                self.logger.info("Detecting sources in %s at %f level" % (
                    image, detection_level))
                data_image = sourcefinder_image_from_accessor(fitsimage)
                results = data_image.extract(det=detection_level)
                self.logger.info("Detected %d sources" % len(results))
                self.logger.info("database = %s", str(database))
                db_image.insert_extracted_sources(results)
                self.logger.info("saved extracted sources to database")
                db_image.associate_extracted_sources(
                    deRuiter_r=radius*
                    config['source_association']['deruiter_radius'])
        return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(source_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
