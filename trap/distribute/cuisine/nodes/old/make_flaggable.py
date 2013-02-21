#                                                         LOFAR IMAGING PIPELINE
#
#                                                            make_flaggable node
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------
from __future__ import with_statement
import os.path
import sys
import imp

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class make_flaggable(LOFARnodeTCP):
    def run(self, infile, makeFLAGwritable):
        with log_time(self.logger):
            if os.path.exists(infile):
                self.logger.info("Processing %s" % (infile))
            else:
                self.logger.error("Dataset %s does not exist" % (infile))
                return 1

            if not os.path.exists(makeFLAGwritable):
                self.logger.error(
                    "file %s not found" % (makeFLAGwritable)
                )
                return 1

            try:
                mFw_module = imp.load_source('mFw_module', makeFLAGwritable)
                mFw_module.makeFlagWritable(infile, '')
            except Exception, e:
                self.logger.warn(str(e))
                return 1

        return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(make_flaggable(jobid, jobhost, jobport).run_with_stored_arguments())
