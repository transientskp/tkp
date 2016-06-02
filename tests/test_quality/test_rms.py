import os
import numpy
from numpy.testing import assert_array_equal, assert_array_almost_equal
import unittest

from tkp.quality.rms import rms_invalid
from tkp import accessors
import tkp.quality
from tkp.quality import statistics
import tkp.telescope.lofar as lofar
from tkp.testutil.decorators import requires_data
from tkp.testutil.data import DATAPATH

core_antennas = os.path.join(DATAPATH, 'lofar/CS001-AntennaArrays.conf')
intl_antennas = os.path.join(DATAPATH, 'lofar/DE601-AntennaArrays.conf')
remote_antennas = os.path.join(DATAPATH, 'lofar/RS106-AntennaArrays.conf')

class TestRms(unittest.TestCase):
    def test_subrgion(self):
        sub = statistics.subregion(numpy.ones((800, 800)))
        self.assertEqual(sub.shape, (400, 400))

    def test_rms(self):
        self.assertEqual(statistics.rms(numpy.ones([4,4])*4), 0)

    def test_clip(self):
        a = numpy.ones([50, 50]) * 10
        a[20, 20] = 20
        clipped = statistics.clip(a)
        check = numpy.array([10] * (50*50-1))
        assert_array_equal(clipped,  check)

    def test_rmsclippedsubregion(self):
        o = numpy.ones((800, 800))
        sub = statistics.subregion(o)
        clip = statistics.clip(sub)
        rms = statistics.rms(clip)
        self.assertEqual(rms, statistics.rms_with_clipped_subregion(o))

    def test_calculate_theoreticalnoise(self):
        # Sample data from a LOFAR image header.
        integration_time = 18654.3 # s
        bandwidth = 200 * 10**3 # Hz
        frequency = 66308593.75 # Hz
        ncore = 23
        nremote = 8
        nintl = 0
        configuration = "LBA_INNER"

        self.assertAlmostEqual(
            lofar.noise.noise_level(frequency, bandwidth, integration_time,
                                    configuration, ncore, nremote, nintl),
            0.01590154516819521 ,# with a calculator!
            places=7
        )

    def test_rms_too_low(self):
        theoretical_noise = 1
        measured_rms = 1e-9
        self.assertTrue(rms_invalid(measured_rms, theoretical_noise))

    def test_rms_too_high(self):
        theoretical_noise = 1
        measured_rms = 1e9
        self.assertTrue(rms_invalid(measured_rms, theoretical_noise))

    def test_rms_valid(self):
        measured_rms = theoretical_noise = 1
        self.assertFalse(rms_invalid(measured_rms, theoretical_noise))


@requires_data(core_antennas)
class testDistances(unittest.TestCase):
    def test_distanses(self):
        """check if all precomputed values match with distances in files"""
        parsed = lofar.antennaarrays.parse_antennafile(core_antennas)
        for conf in ("LBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0",
                     "LBA_SPARSE1"):
            ds = lofar.antennaarrays.shortest_distances(parsed[conf],
                                                        parsed["LBA"])
            assert_array_almost_equal(ds,
                  lofar.antennaarrays.core_dipole_distances[conf], decimal=2)

        parsed = lofar.antennaarrays.parse_antennafile(intl_antennas)
        for conf in ("LBA", "LBA_INNER", "LBA_OUTER"):
            ds = lofar.antennaarrays.shortest_distances(parsed[conf],
                                                        parsed["LBA"])
            assert_array_almost_equal(ds,
                  lofar.antennaarrays.intl_dipole_distances[conf], decimal=2)

        parsed = lofar.antennaarrays.parse_antennafile(remote_antennas)
        for conf in ("LBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0",
                     "LBA_SPARSE1", "LBA_X", "LBA_X"):
            ds = lofar.antennaarrays.shortest_distances(parsed[conf],
                                                        parsed["LBA"])
            assert_array_almost_equal(ds,
                  lofar.antennaarrays.remote_dipole_distances[conf], decimal=2)


if __name__ == '__main__':
    unittest.main()
