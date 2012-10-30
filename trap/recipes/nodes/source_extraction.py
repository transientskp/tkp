import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
import trap.source_extraction

class source_extraction(LOFARnodeTCP):
    def run(self, image,  parset, tkpconfigdir=None):
        """Extract sources from a FITS image
        Args:
            - image: FITS filename
            - parset: parameter set *filename* containg at least the
                  detection threshold and the source association
                  radius, the last one in units of the de Ruiter
                  radius.
        """
        self.outputs['image_id'] = trap.source_extraction.extract_sources(image, parset, tkpconfigdir)

        return 0

if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(source_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
