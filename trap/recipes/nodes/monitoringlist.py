import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
import trap.monitoringlist

class monitoringlist(LOFARnodeTCP):
    def run(self, image_id):
        trap.monitoringlist.update_monitoringlist(image_id)
        return 0

if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(monitoringlist(jobid, jobhost, jobport).run_with_stored_arguments())
