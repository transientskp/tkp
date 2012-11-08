import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
import trap.classification

class classification(LOFARnodeTCP):

    def run(self, transient, parset, tkpconfigdir=None):

        with log_time(self.logger):
            trap.classification.logger = self.logger
            self.outputs['transient'] = trap.classification.classify(transient, parset, tkpconfigdir)
        return 0

if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(classification(jobid, jobhost, jobport).run_with_stored_arguments())
