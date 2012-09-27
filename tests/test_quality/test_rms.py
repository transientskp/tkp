__author__ = 'Gijs Molenaar'

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
import re
import math
from tkp.utility import accessors
from tkp.quality import statistics
import tkp.lofar.noise
import tkp.config
import tkp.lofar.antennaarrays
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import requires_data
import numpy
from numpy.testing import assert_array_equal, assert_almost_equal


DATAPATH = tkp.config.config['test']['datapath']
bad_file = os.path.join(DATAPATH, 'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band5.corr.fits')
good_file = os.path.join(DATAPATH, 'quality/noise/good/home-pcarrol-msss-L086+69-analysis-band2.corr.fits')
antenna_file = os.path.join(DATAPATH, 'lofar/CS001-AntennaArrays.conf')

#numpy.seterr(all='raise')

@requires_data(antenna_file)
@requires_data(bad_file)
@requires_data(good_file)
class TestNoise(unittest.TestCase):
    def setUp(self):
        self.bad_image = accessors.FitsFile(bad_file, plane=0)
        self.good_image = accessors.FitsFile(good_file, plane=0)

    def testRms(self):
        self.assertEquals(statistics.rms(numpy.ones([4,4])*4), 0)

    def testClip(self):
        a = numpy.ones([50, 50]) * 10
        a[20, 20] = 20
        clipped = statistics.clip(a)
        check = numpy.array([10] * (50*50-1))
        assert_array_equal(clipped,  check)

    def testTheoreticalMaxValue(self):
        frequency = self.good_image.freqeff

        #integration_time = self.good_image.inttime
        integration_time = 18654.3 # s

        #bandwidth = self.good_image.freqbw
        subbandwidth = 200 * 10**3 # Hz

        ncore = 23 # ~
        nremote = 8 # ~
        nintl = 0
        num_subband = 10
        num_channels = 64
        configuration = "LBA_INNER"

        # extract pixel size from HISTORY junk in fits header
        history = self.bad_image.header['HISTORY*']
        xy_line = [i for i in history.values() if 'cellx' in i][0]
        extracted = re.search(r"cellx='(?P<x>\d+).*celly='(?P<y>\d+)", xy_line).groupdict()
        xsize = int(extracted['x'])
        ysize = int(extracted['y'])
        bmaj = self.bad_image.header['BMAJ'] * 3600 # convert from degrees to arcsec
        bmin = self.bad_image.header['BMIN'] * 3600

        bmaj_scaled = bmaj / xsize
        bmin_scaled = bmin / ysize
        area = math.pi * bmaj_scaled * bmin_scaled

        noise_level = tkp.lofar.noise.noise_level(frequency, subbandwidth, integration_time, configuration, num_subband,
                        num_channels, ncore, nremote, nintl)

        print noise_level

    def testRmsFits(self):
        bad_rms = statistics.rms(self.bad_image.data)
        good_rms = statistics.rms(self.good_image.data)

    def testDistanses(self):
        parsed = tkp.lofar.antennaarrays.parse_antennafile(antenna_file)
        for conf in "LBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0", "LBA_SPARSE1":
            ds = tkp.lofar.antennaarrays.shortest_distances(parsed[conf], parsed["LBA"])
            assert_almost_equal(ds, tkp.lofar.antennaarrays.dipole_distances[conf], decimal=2)

if __name__ == '__main__':
    unittest.main()
