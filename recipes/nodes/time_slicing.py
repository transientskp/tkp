#                                                       LOFAR TRANSIENTS PIPELINE
#
# ------------------------------------------------------------------------------

from __future__ import with_statement

import os
import sys

from pyrap.quanta import quantity
from pyrap.tables import table

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class time_slicing(LOFARnodeTCP):

    # --------------------------------------------------------------------------
    def run(self, path, host, resultsdir, start_time, end_time):
        with log_time(self.logger):
            self.logger.info("Processing %s" % (path,))

            #    Bail out if destination exists (can thus resume a partial run).
            #                                            Should be configurable?
            # ------------------------------------------------------------------
            try:
                os.mkdir(resultsdir)
            except OSError:
                pass  # directory already created by another node process
            filename = os.path.basename(path)
            output = os.path.join(resultsdir, filename)

            # Copy that section of the input MS and only image that.
            # --------------------------------------------------------------
            query = []
            start_time = quantity(float(start_time), 's')
            query.append("TIME > %f" % start_time.get('s').get_value())
            end_time = quantity(float(end_time), 's')
            query.append("TIME < %f" % end_time.get('s').get_value())
            query = " AND ".join(query)
            #                             Select relevant section of MS.
            # ----------------------------------------------------------
            self.logger.debug("Query for %s is %s" % (output, query))
            t = table(path, ack=False)
            t.query(query, name=output)
            #       Patch updated information into imager configuration.
            # ----------------------------------------------------------
            #t.close()
            self.outputs['output'] = (host, output)
            
            return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(time_slicing(jobid, jobhost, jobport).run_with_stored_arguments())
