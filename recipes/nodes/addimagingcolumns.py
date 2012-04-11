#                                              LOFAR TRANSIENTS IMAGING PIPELINE
#
#                                                   Imager-columns adding recipe
#                                                                Evert Rol, 2012
#                                                      software@transientskp.org
# ------------------------------------------------------------------------------

# See also http://lus.lofar.org/forum/index.php?topic=873.0

from __future__ import with_statement
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from tempfile import mkdtemp
import os
import sys

import pyrap.tables
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class addimagingcolumns(LOFARnodeTCP):
    def run(self, ms):
        """Add imaging columns to the measurement set

        Args:

            - ms: measurement set
        """
        
        with log_time(self.logger):
            self.logger.info("Processing %s" % (ms,))
            pyrap.tables.addImagingColumns(ms, ack=False)
            
            return 0


if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(addimagingcolumns(jobid, jobhost, jobport).run_with_stored_arguments())
