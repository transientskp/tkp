import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
import trap.monitoringlist

class monitoringlist(LOFARnodeTCP):
    def run(self, filename, image_id, dataset_id):
        trap.monitoringlist.monitoringlist(filename, image_id, dataset_id)
        return 0

if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(monitoringlist(jobid, jobhost, jobport).run_with_stored_arguments())
