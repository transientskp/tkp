__author__ = 'Gijs Molenaar'

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
from tkp.utility import accessors
from tkp.quality import statistics
import tkp.lofar.noise
import tkp.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import requires_data
import numpy
from numpy.testing import assert_array_equal, assert_almost_equal

fits_file = '/home/gijs/Data/antonia_april/original/img1.fits'
antenna_file = '/home/gijs/Work/lofar_system_software/LOFAR/MAC/Deployment/data/StaticMetaData/AntennaArrays/CS001-AntennaArrays.conf'

DATAPATH = tkp.config.config['test']['datapath']

bad_file = os.path.join(DATAPATH, 'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band1.corr.fits')
good_file = os.path.join(DATAPATH, 'quality/noise/good/home-pcarrol-msss-L086+69-analysis-band2.corr.fits')

numpy.seterr(all='raise')

@requires_data(fits_file)
@requires_data(antenna_file)
@requires_data(bad_file)
@requires_data(good_file)
#@unittest.skip
class test_maps(unittest.TestCase):
    def setUp(self):
        self.bad_image = accessors.FitsFile(bad_file, plane=0)
        self.good_image = accessors.FitsFile(good_file, plane=0)

    def testRms(self):
        rms = statistics.rms(self.good_image.data)
        #self.assertEquals(statistics.rms(numpy.ones([4,4])*4), 16)

    def testClip(self):
        a = numpy.ones([800, 800]) * 200
        a[400, 400] = 1000
        clipped = statistics.clip(a)
        check = numpy.ones([800, 800])
        check[400,400] = 0
        assert_almost_equal(clipped,  check, decimal=5)

    def testTheoreticalMaxValue(self):
        bandwidth = self.good_image.freqbw
        freq = self.good_image.freqeff
        integration_time = self.good_image.inttime

        # TODO: somehow these are 0 in some images sometimes?
        if bandwidth == 0.0: bandwidth = 1.0
        if integration_time == 0.0: integration_time = 1.0

        # TODO: where can I fond the number of core stations etc in a FITS file?

        frequencies_lba = [x*10**6 for x in [15, 30, 45, 60, 75]]
        frequencies_hba = [x*10**6 for x in [120, 150, 180, 210, 240]]
        configurations = ["HBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0", "LBA_SPARSE1"]
        parsed = tkp.lofar.noise.parse_antennafile(antenna_file)

        for configuration in configurations:
            print "\n" + configuration
            if configuration.startswith("LBA"):
                freqiencies = frequencies_lba
                full_array = parsed["LBA"]
            else:
                freqiencies = frequencies_hba
                full_array = parsed["HBA"]
            positions = parsed[configuration]
            for frequency in freqiencies:
                distances = tkp.lofar.noise.shortest_distances(positions, full_array)
                aeff = sum([tkp.lofar.noise.Aeff_dipole(frequency, x) for x in distances])
                noise_level = tkp.lofar.noise.system_sensitivity(frequency, aeff)
                print frequency, "\t", aeff

    def testRmsFits(self):
        # with clipping
        bad_rms = statistics.rms(self.bad_image.data)
        good_rms = statistics.rms(self.good_image.data)

        # without clipping
        bad_mask = statistics.clip(self.bad_image.data)
        bad_rms = statistics.rms(self.bad_image.data, bad_mask)

        good_mask = statistics.clip(self.good_image.data)
        good_rms = statistics.rms(self.good_image.data, good_mask)



if __name__ == '__main__':
    unittest.main()
