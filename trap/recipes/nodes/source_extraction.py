import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
import trap.source_extraction

class source_extraction(LOFARnodeTCP):
    def run(self, image, dataset_id, parset, store_images, mongo_host, mongo_port, mongo_db, tkpconfigdir=None):
        """Extract sources from a FITS image
        Args:

            - image: FITS filename

            - dataset_id: dataset to which image belongs

            - parset: parameter set *filename* containg at least the
                  detection threshold and the source association
                  radius, the last one in units of the de Ruiter
                  radius.

            - storage_images: bool. Store images to MongoDB database if True.

            - mongo_host/port/db: details of MongoDB to use if store_images is
              True.
        """
        self.outputs['image_id'] = trap.source_extraction.extract_sources(image, dataset_id, parset, store_images,
                                            mongo_host, mongo_port, mongo_db, tkpconfigdir)

        return 0

if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(source_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
