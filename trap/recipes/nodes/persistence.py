import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
import trap.source_extraction

class persistance(LOFARnodeTCP):
    def run(self, image, dataset_id, parset, store_images, mongo_host, mongo_port, mongo_db, tkpconfigdir=None):
        """Extract sources from a FITS image
        Args:
            - image: FITS filename
            - dataset_id: dataset to which image belongs
            - storage_images: bool. Store images to MongoDB database if True.
            - mongo_host/port/db: details of MongoDB to use if store_images is  True.
        """
        self.outputs['image_id'] = trap.persistence.store(image, dataset_id, store_images, mongo_host, mongo_port,
            mongo_db, tkpconfigdir)
        return 0

if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(persistance(jobid, jobhost, jobport).run_with_stored_arguments())
