import sys
from contextlib import closing
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
import tkp.quality
from tkp.database import DataBase, DataSet
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import dbimage_from_accessor

class quality_check(LOFARnodeTCP):
    def run(self, image, dataset_id):
        with log_time(self.logger):
            with closing(DataBase()) as database:
                dataset = DataSet(id=dataset_id, database=database)
                fitsimage = FITSImage(image)
                db_image = dbimage_from_accessor(dataset=dataset,  image=fitsimage)
                rms = rms_with_clipped_subregion(fitsimage.data)

                # todo: get this stuff from header
                noise = noise_level(45*10**6, 200*10**3, 18654, "LBA_INNER", 10, 24, 23, 8, 0)
                
                if tkp.quality.rms_valid(rms, noise):
                    self.outputs['image_id'] = db_image.id
                else:
                    self.outputs['image_id'] = None
        return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(quality_check(jobid, jobhost, jobport).run_with_stored_arguments())