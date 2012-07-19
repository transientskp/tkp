#                                             LOFAR TRANSIENT DETECTION PIPELINE
#
#                                                                Evert Rol, 2011
#                                                          evert.astro@gmail.com
# ------------------------------------------------------------------------------

from __future__ import with_statement

import os
import sys
from contextlib import closing

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


BOX_IN_BEAMPIX = 10 #HARDCODING - FIXME! (see also 'image' unit test)


class monitoringlist(LOFARnodeTCP):
    """
    """

    def run(self, filename, image_id, dataset_id, tkpconfigdir=None):
        if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
            os.environ['TKPCONFIGDIR'] = tkpconfigdir
        from tkp.config import config
        from tkp.database.database import DataBase
        from tkp.database.dataset import DataSet
        from tkp.database.dataset import Image as DBImage
        from tkp.utility.accessors import FITSImage
        from tkp.utility.accessors import dbimage_from_accessor
        from tkp.utility.accessors import sourcefinder_image_from_accessor
        """

        Args:

            - filename: FITS file
            
            - image_id: database image id
            
            - dataset_id: dataset to which the image belongs

        """
        
        with log_time(self.logger):
            with closing(DataBase()) as database:
                # Obtain the list of sources to be monitored (and not already
                # detected) for this image
                fitsimage = FITSImage(filename)
                
                ##TO DO: would prefer it if there were an easy way for the image
                ## to determine its parent dataset without being spoon fed.
                ## -This would cut down on required recipe arguments and generally
                ##    make it harder to screw up.
                dataset = DataSet(id = dataset_id, database=database)
                db_image = DBImage(id=image_id, database=database, dataset=dataset)
#                db_image.update()
                sources = db_image.monitoringsources()
                # Run the source finder on these sources
                if len(sources):
                    self.logger.info("Measuring %d undetected monitoring sources: %s",
                                     len(sources), str(sources))
                    data_image = sourcefinder_image_from_accessor(fitsimage)
                    results = data_image.fit_fixed_positions(
                        [(source[0], source[1]) for source in sources],
                        boxsize=BOX_IN_BEAMPIX*max(data_image.beam[0], data_image.beam[1]))
                    # Filter out the bad ones, and combines with xtrsrc_ids
                    results = [(source[2], source[3], result.serialize()) for source, result in
                               zip(sources, results) if result is not None]
                    db_image.insert_monitored_sources(results)
                
        return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(monitoringlist(jobid, jobhost, jobport).run_with_stored_arguments())
