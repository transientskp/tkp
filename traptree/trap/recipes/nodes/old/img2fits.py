from __future__ import with_statement
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from tempfile import mkdtemp
import os
import sys

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class img2fits(LOFARnodeTCP):
    #                 Handles running a single cimager process on a compute node
    # --------------------------------------------------------------------------
    def run(self, image, ms, fitsfile=None, tkpconfigdir=None):
        if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
            os.environ['TKPCONFIGDIR'] = tkpconfigdir
        import tkp.utility.fits
        """Convert a CASA image to a FITS image

        Args:

            - image: image name

            - ms: original measurement set name; needed for meta data


        Kwargs:

            - fitsfile: optional output name for FITS file

        """
        
        with log_time(self.logger):
            self.logger.info("Processing %s" % (image,))
            tkp.utility.fits.convert(image, ms, fitsfile)
            
            return 0


if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(img2fits(jobid, jobhost, jobport).run_with_stored_arguments())
