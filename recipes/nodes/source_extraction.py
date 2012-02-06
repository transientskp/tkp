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

from lofar.parameterset import parameterset
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class source_extraction(LOFARnodeTCP):
    """
    Extract sources from a FITS image
    """

    def run(self, image, dataset_id, parset, tkpconfigdir=None):
        if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
            os.environ['TKPCONFIGDIR'] = tkpconfigdir
        import tkp
        from tkp.config import config
        from tkp.database.database import DataBase
        from tkp.database.dataset import DataSet
        from tkp.utility.accessors import FITSImage
        from tkp.utility.accessors import dbimage_from_accessor
        from tkp.utility.accessors import sourcefinder_image_from_accessor
        """

        Args:

            - image: FITS filename

            - dataset_id: dataset to which image belongs

            - parset: parameter set *filename* containg at least the
                  detection threshold and the source association
                  radius, the last one in units of the de Ruiter
                  radius.

        """
        
        with log_time(self.logger):
            with closing(DataBase()) as database:
                parset = parameterset(parset)
                dataset = DataSet(id=dataset_id, database=database)
                fitsimage = FITSImage(image)
                db_image = dbimage_from_accessor(dataset=dataset,
                                                 image=fitsimage)
                self.logger.info("Detecting sources in %s at %f level", 
                                 image, parset.getFloat('detection.threshold'))
                data_image = sourcefinder_image_from_accessor(fitsimage)
                results = data_image.extract(det=parset.getFloat('detection.threshold'))
                self.logger.info("Detected %d sources", len(results))
                self.logger.info("database = %s", str(database))
                db_image.insert_extracted_sources(results)
                self.logger.info("saved extracted sources to database")
                deRuiter_r = (parset.getFloat('association.radius') *
                              config['source_association']['deruiter_radius'])
                db_image.associate_extracted_sources(deRuiter_r=deRuiter_r)
                db_image.match_monitoringlist(update_image_column=True,
                     assoc_r=deRuiter_r, mindistance=30)
                self.outputs['image_id'] = db_image.id
        return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(source_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
