import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
import trap.quality


class quality_check(LOFARnodeTCP):
    def run(self, image_id, parset_file):
        with log_time(self.logger):
            self.outputs['image_id'] = image_id
            trap.quality.logger = self.logger
            self.outputs['pass'] = trap.quality.noise(image_id, parset_file)
        return 0

if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(quality_check(jobid, jobhost, jobport).run_with_stored_arguments())
