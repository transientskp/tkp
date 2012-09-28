__author__ = 'Gijs Molenaar'

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
import re
import math
from tkp.utility import accessors
import tkp.quality
from tkp.quality import statistics
import tkp.lofar.noise
import tkp.config
import tkp.lofar.antennaarrays
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import requires_data
import numpy
from numpy.testing import assert_array_equal, assert_almost_equal


DATAPATH = tkp.config.config['test']['datapath']

core_antennas = os.path.join(DATAPATH, 'lofar/CS001-AntennaArrays.conf')
intl_antennas = os.path.join(DATAPATH, 'lofar/DE601-AntennaArrays.conf')
remote_antennas = os.path.join(DATAPATH, 'lofar/RS106-AntennaArrays.conf')

bad_files = [os.path.join(DATAPATH, 'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band%i.corr.fits' % i) for i in range(1, 8)]
good_files = [os.path.join(DATAPATH, 'quality/noise/good/home-pcarrol-msss-L086+69-analysis-band%i.corr.fits' % i) for i in range(2, 8)]

#numpy.seterr(all='raise')

@requires_data(core_antennas)
@requires_data(bad_files[0])
class TestNoise(unittest.TestCase):
    def testRms(self):
        """ basic check if RMS calculation works
        """
        self.assertEquals(statistics.rms(numpy.ones([4,4])*4), 0)

    def testClip(self):
        """ basic check if clipping works"""
        a = numpy.ones([50, 50]) * 10
        a[20, 20] = 20
        clipped = statistics.clip(a)
        check = numpy.array([10] * (50*50-1))
        assert_array_equal(clipped,  check)

    def testTheoreticalMaxValue(self):
        good_image = accessors.FitsFile(good_files[0], plane=0)
        frequency = good_image.freqeff

        #integration_time = self.good_image.inttime
        integration_time = 18654.3 # s

        #bandwidth = self.good_image.freqbw
        subbandwidth = 200 * 10**6 # Hz

        ncore = 23 # ~
        nremote = 8 # ~
        nintl = 0
        num_subband = 10
        num_channels = 64
        configuration = "LBA_INNER"

        noise_level = tkp.lofar.noise.noise_level(frequency, subbandwidth, integration_time, configuration, num_subband,
                        num_channels, ncore, nremote, nintl)

        # TODO: find a nice way to test this
        print noise_level

    def testRmsFits(self):
        # TODO: find a nice way to test this
        for bad_file in bad_files:
            bad_image = accessors.FitsFile(bad_file, plane=0)
            beam_correction = statistics.beam_correction(bad_image)
            bad_rms = statistics.rms(bad_image.data)
            #print bad_file, bad_rms, bad_rms/beam_correction

        for good_file in good_files:
            good_image = accessors.FitsFile(good_file, plane=0)
            beam_correction = statistics.beam_correction(good_image)
            good_rms = statistics.rms(good_image.data)
            #print good_file, good_rms, good_rms/beam_correction


    def testDistanses(self):
        """
        check if all precomputed values match with distances in files
        """
        parsed = tkp.lofar.antennaarrays.parse_antennafile(core_antennas)
        for conf in "LBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0", "LBA_SPARSE1":
            ds = tkp.lofar.antennaarrays.shortest_distances(parsed[conf], parsed["LBA"])
            assert_almost_equal(ds, tkp.lofar.antennaarrays.core_dipole_distances[conf], decimal=2)

        parsed = tkp.lofar.antennaarrays.parse_antennafile(intl_antennas)
        for conf in "LBA", "LBA_INNER", "LBA_OUTER":
            ds = tkp.lofar.antennaarrays.shortest_distances(parsed[conf], parsed["LBA"])
            assert_almost_equal(ds, tkp.lofar.antennaarrays.intl_dipole_distances[conf], decimal=2)

        parsed = tkp.lofar.antennaarrays.parse_antennafile(remote_antennas)
        for conf in "LBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0", "LBA_SPARSE1", "LBA_X", "LBA_X":
            ds = tkp.lofar.antennaarrays.shortest_distances(parsed[conf], parsed["LBA"])
            assert_almost_equal(ds, tkp.lofar.antennaarrays.remote_dipole_distances[conf], decimal=2)



if __name__ == '__main__':
    unittest.main()
