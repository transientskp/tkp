from __future__ import with_statement
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
import shutil, os.path
import sys

class parmdb(LOFARnodeTCP):
    def run(self, infile, pdb):
        with log_time(self.logger):
            if os.path.exists(infile):
                self.logger.info("Processing %s" % (infile))
            else:
                self.logger.error("Dataset %s does not exist" % (infile))
                return 1

            output = os.path.join(infile, os.path.basename(pdb))

            # Remove any old parmdb database
            shutil.rmtree(output, ignore_errors=True)

            # And copy the new one into place
            shutil.copytree(pdb, output)

        return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(parmdb(jobid, jobhost, jobport).run_with_stored_arguments())
