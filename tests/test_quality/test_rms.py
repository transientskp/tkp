import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import numpy
from numpy.testing import assert_array_equal, assert_array_almost_equal
from tkp.utility import accessors
import tkp.quality
from tkp.quality import statistics
import tkp.lofar.noise
import tkp.config
import tkp.lofar.antennaarrays
from tkp.testutil.decorators import requires_data


DATAPATH = tkp.config.config['test']['datapath']

core_antennas = os.path.join(DATAPATH, 'lofar/CS001-AntennaArrays.conf')
intl_antennas = os.path.join(DATAPATH, 'lofar/DE601-AntennaArrays.conf')
remote_antennas = os.path.join(DATAPATH, 'lofar/RS106-AntennaArrays.conf')

bad_file = os.path.join(DATAPATH, 'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits')
good_file = os.path.join(DATAPATH, 'quality/noise/good/home-pcarrol-msss-L086+69-analysis-band6.corr.fits')

#numpy.seterr(all='raise')

@requires_data(bad_file)
@requires_data(good_file)
class TestRms(unittest.TestCase):
    def test_subrgion(self):
        sub = statistics.subregion(numpy.ones((800, 800)))
        self.assertEqual(sub.shape, (400, 400))

    def test_rms(self):
        self.assertEquals(statistics.rms(numpy.ones([4,4])*4), 0)

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

    def test_theoreticalnoise(self):
        good_image = accessors.open(good_file)
        bad_image = accessors.open(bad_file)
        frequency = good_image.freqeff

        # this stuff should be in the header of a LOFAR image some day
        integration_time = 18654.3 # s, should be self.good_image.inttime some day
        subbandwidth = 200 * 10**3 # Hz, shoud probably be self.good_image.freq_bw some day
        ncore = 23 # ~
        nremote = 8 # ~
        nintl = 0
        num_subband = 10
        num_channels = 64
        configuration = "LBA_INNER"

        noise = tkp.lofar.noise.noise_level(frequency, subbandwidth, integration_time, configuration, num_subband,
                        num_channels, ncore, nremote, nintl)
        rms_good = statistics.rms_with_clipped_subregion(good_image.data)
        rms_bad = statistics.rms_with_clipped_subregion(bad_image.data)

        self.assertFalse(tkp.quality.rms_invalid(rms_good, noise))
        self.assertTrue(tkp.quality.rms_invalid(rms_bad, noise))

    def test_rms_fits(self):
        accessors.open(good_file)


@requires_data(core_antennas)
class testDistances(unittest.TestCase):
    def test_distanses(self):
        """check if all precomputed values match with distances in files"""
        parsed = tkp.lofar.antennaarrays.parse_antennafile(core_antennas)
        for conf in "LBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0", "LBA_SPARSE1":
            ds = tkp.lofar.antennaarrays.shortest_distances(parsed[conf], parsed["LBA"])
            assert_array_almost_equal(ds, tkp.lofar.antennaarrays.core_dipole_distances[conf], decimal=2)

        parsed = tkp.lofar.antennaarrays.parse_antennafile(intl_antennas)
        for conf in "LBA", "LBA_INNER", "LBA_OUTER":
            ds = tkp.lofar.antennaarrays.shortest_distances(parsed[conf], parsed["LBA"])
            assert_array_almost_equal(ds, tkp.lofar.antennaarrays.intl_dipole_distances[conf], decimal=2)

        parsed = tkp.lofar.antennaarrays.parse_antennafile(remote_antennas)
        for conf in "LBA", "LBA_INNER", "LBA_OUTER", "LBA_SPARSE0", "LBA_SPARSE1", "LBA_X", "LBA_X":
            ds = tkp.lofar.antennaarrays.shortest_distances(parsed[conf], parsed["LBA"])
            assert_array_almost_equal(ds, tkp.lofar.antennaarrays.remote_dipole_distances[conf], decimal=2)


if __name__ == '__main__':
    unittest.main()
