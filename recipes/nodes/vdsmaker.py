#                                                         LOFAR IMAGING PIPELINE
#
#                                                                  vdsmaker node
#                                                         John Swinbank, 2009-10
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
import os
import sys

from lofarpipe.support.lofarexceptions import ExecutableMissing
from lofarpipe.support.utilities import create_directory, log_time
from lofarpipe.support.utilities import catch_segfaults
from lofarpipe.support.lofarnode import LOFARnodeTCP

class vdsmaker(LOFARnodeTCP):
    """
    Make a VDS file for the input MS in a specificed location.
    """
    def run(self, infile, clusterdesc, outfile, executable):
        with log_time(self.logger):
            if os.path.exists(infile):
                self.logger.info("Processing %s" % (infile))
            else:
                self.logger.error("Dataset %s does not exist" % (infile))
                return 1

            try:
                if not os.access(executable, os.X_OK):
                    raise ExecutableMissing(executable)
                cmd = [executable, clusterdesc, infile, outfile]
                result = catch_segfaults(cmd, None, None, self.logger).returncode
                self.outputs["result"] = result
            except ExecutableMissing, e:
                self.logger.error("%s not found" % (e.args[0]))
                return 1
            except CalledProcessError, e:
                # For CalledProcessError isn't properly propagated by IPython
                # Temporary workaround...
                self.logger.error(str(e))
                return 1

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(vdsmaker(jobid, jobhost, jobport).run_with_stored_arguments())
