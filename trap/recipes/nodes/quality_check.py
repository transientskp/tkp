import sys
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
import tkp.quality
import tkp.database.quality
from tkp.database import DataBase, DataSet
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import dbimage_from_accessor
#from lofar.parameterset import parameterset
from lofarpipe.support.parset import parameterset

class quality_check(LOFARnodeTCP):
    def run(self, image, dataset_id, parset):
        log_time(self.logger)
        self.database = DataBase()
        self.dataset = DataSet(id=dataset_id, database=self.database)
        self.fitsimage = FITSImage(image, plane=0)
        self.db_image = dbimage_from_accessor(dataset=self.dataset,  image=self.fitsimage)
        self.parset = parameterset(parset)
        self.rms()
        return 0

    def rms(self):

        sigma = self.parset.getInt('sigma', 3)
        f = self.parset.getInt('f', 4)
        low_bound = self.parset.getFloat('low_bound', 1)
        high_bound = self.parset.getInt('high_bound', 50)
        frequency = self.parset.getInt('frequency', 45*10**6)
        subbandwidth = self.parset.getInt('subbandwidth', 200*10**3)
        intgr_time = self.parset.getFloat('intgr_time', 18654)
        configuration = self.parset.getString('configuration', "LBA_INNER")
        subbands = self.parset.getInt('subbands', 10)
        channels = self.parset.getInt('channels', 64)
        ncore = self.parset.getInt('ncore', 24)
        nremote = self.parset.getInt('nremote',16)
        nintl = self.parset.getInt('nintl', 8)

        rms = rms_with_clipped_subregion(self.fitsimage.data, sigma=sigma, f=f)

        noise = noise_level(frequency, subbandwidth, intgr_time, configuration, subbands, channels, ncore, nremote, nintl)

        if tkp.quality.rms_valid(rms, noise, low_bound=low_bound, high_bound=high_bound):
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