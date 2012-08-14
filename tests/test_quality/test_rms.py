__author__ = 'Gijs Molenaar'

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
from tkp.utility import accessors
from tkp.quality import rms
import tkp.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import requires_data
import numpy
from numpy.testing import assert_array_equal, assert_almost_equal


DATAPATH = tkp.config.config['test']['datapath']



@requires_data(os.path.join(DATAPATH, 'UNCORRELATED_NOISE.FITS'))
class test_maps(unittest.TestCase):
    def setUp(self):
        self.uncorr_map = accessors.FitsFile(os.path.join(DATAPATH, 'UNCORRELATED_NOISE.FITS'))

    def testRms(self):
        #self.rms = rms.rms(self.uncorr_map.data)
        self.assertEquals(rms.rms(numpy.ones([4,4])*4), 16)

    def testClip(self):
        a = numpy.ones([800, 800]) * 200
        a[400, 400] = 1000
        clipped = rms.clip(a)
        check = numpy.ones([800, 800]) * 200
        check[400, 400] = 203
        assert_almost_equal(clipped,  check, decimal=5)

    def testTheoreticalMaxValue(self):
        bandwidth = self.uncorr_map.freqbw
        freq = self.uncorr_map.freqeff

        # TODO: integration time is 0? that's not correct right?
        integration_time = self.uncorr_map.inttime
        integration_time = 1
        rms.theoretical_max_rms(freq, bandwidth, integration_time)


if __name__ == '__main__':
    unittest.main()
