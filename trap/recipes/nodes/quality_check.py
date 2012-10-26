import sys
from contextlib import closing
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
import tkp.quality
import tkp.database.quality
from tkp.database import DataBase, DataSet
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import dbimage_from_accessor

class quality_check(LOFARnodeTCP):
    def run(self, image, dataset_id):
        log_time(self.logger)
        self.database = DataBase()
        self.dataset = DataSet(id=dataset_id, database=self.database)
        self.fitsimage = FITSImage(image)
        self.db_image = dbimage_from_accessor(dataset=self.dataset,  image=self.fitsimage)
        self.rms()
        return 0

    def rms(self):
        rms = rms_with_clipped_subregion(self.fitsimage.data)

        # todo: get this stuff from header
        noise = noise_level(45*10**6, 200*10**3, 18654, "LBA_INNER", 10, 24, 23, 8, 0)

        if tkp.quality.rms_valid(rms, noise):
            self.outputs['image_id'] = self.db_image.id
        else:
            ratio = rms / noise
            reason = "noise level is %s times theoretical value" % ratio
            self.logger.info("image %s invalid: %s " % (self.db_image.id, reason) )
            tkp.database.quality.reject(self.database.connection, self.db_image.id, tkp.database.quality.reason['rms'], reason)
            self.outputs['image_id'] = None


if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(quality_check(jobid, jobhost, jobport).run_with_stored_arguments())