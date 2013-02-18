#! /usr/bin/env python

"""

Unit test for feature extraction, used in the classification pipeline

Some unittests also serve as examples.For example, the background
calculation tests (test_calc_background) show what happens when not
enough background data is/are available.

Note on the multiplications in the assertAlmostEqual statements:
because the test simply compares to a default precision of 1e-7, a
number like 1e-8 will almost always be equal to any other small
number. Multiplying by the order of magnitude ascertains the
comparison is more approritate.
"""

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import numpy
from datetime import datetime
from datetime import timedelta
from tkp.classification.features import lightcurve as lcmod
from tkp.classification.transient import DateTime


class TestLightcurve(unittest.TestCase):
    """  """

    def setUp(self):
        # create test data
        self.timezero = datetime(2010, 10, 1, 12, 0, 0)
        self.lightcurve = lcmod.LightCurve(
            taustart_tss=numpy.array([self.timezero + timedelta(0, s) for s in
                      numpy.arange(0, 30*60, 60, dtype=numpy.float)]),
            tau_times=numpy.ones(30, dtype=numpy.float) * 60,
            fluxes=numpy.ones(30, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(30, dtype=numpy.float) * 1e-8,
            srcids=numpy.arange(0, 30)
        )
        # add errors, but not entirely randomly
        # usage of eg numpy.random.normal has shown that this may
        # result in the occasional *failure* of a unit test, which
        # should be expected for *random* data (but is hard to catch
        # in a unit test).
        errors = [5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9, 8e-9, -8e-9,
                  2e-8, -2e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
                  2.5e-8, -2.5e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
                  1.5e-8, -1.5e-8, 5e-9, -5e-9, 1e-8, -1e-8]
        self.lightcurve.fluxes += numpy.array(errors)


    def tearDown(self):
        pass

    def test_calc_background(self):
        lc = self.lightcurve
        lc.reset()

        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.)
        self.assertAlmostEqual(background['sigma']*1e8, 1.14138451921)
        self.assertEqual(background['indices'].all(), True)

        # Corner cases first
        # transient at start
        lc.reset()
        lc.fluxes[0] *= 4.
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 0.999827586)
        self.assertAlmostEqual(background['sigma']*1e8, 1.1576049676)
        self.assertEqual(background['indices'][0], False)
        self.assertEqual(background['indices'][1:].all(), True)

        # transient on first two light curve points
        lc.reset()
        lc.fluxes[1] *= 2.
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.)
        self.assertAlmostEqual(background['sigma']*1e8, 1.17504925035)
        self.assertEqual(background['indices'][2:].all(), True)
        self.assertEqual(background['indices'][0:2].any(), False)

        # transient near very end
        lc.reset()
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 4.
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.0003448276)
        self.assertAlmostEqual(background['sigma']*1e8, 1.145574049)
        self.assertEqual(background['indices'][:-1].all(), True)
        self.assertEqual(background['indices'][-1], False)

        # transient at last two light curve points
        lc.reset()
        lc.fluxes[-2] *= 2.
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.)
        self.assertAlmostEqual(background['sigma']*1e8, 1.1511668798)
        self.assertEqual(background['indices'][:-2].all(), True)
        self.assertEqual(background['indices'][-2:].any(), False)

        # single peak transient
        lc.reset()
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 4.
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 0.9997241379)
        self.assertAlmostEqual(background['sigma']*1e8, 1.151364579)
        self.assertEqual(background['indices'][6], False)
        self.assertEqual(background['indices'][:6].all(), True)
        self.assertEqual(background['indices'][7:].all(), True)

        # longer transient
        lc.reset()
        lc.fluxes[5] *= 2.
        lc.fluxes[7] *= 2.
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.000185185)
        self.assertAlmostEqual(background['sigma']*1e8, 1.18062468)
        self.assertEqual(background['indices'][:5].all(), True)
        self.assertEqual(background['indices'][8:].all(), True)
        self.assertEqual(background['indices'][5:8].any(), False)

        # Double peaked transient
        lc.reset()
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 4.
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.000416667)
        self.assertAlmostEqual(background['sigma']*1e8, 1.009914618)
        self.assertEqual(background['indices'][:5].all(), True)
        self.assertEqual(background['indices'][8:15].all(), True)
        self.assertEqual(background['indices'][18:].all(), True)
        self.assertEqual(background['indices'][5:8].any(), False)
        self.assertEqual(background['indices'][15:18].any(), False)

        # steadily increasing background
        lc.reset()
        lc.fluxes = numpy.linspace(1.e-6, 1.e-4, 30)
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.)
        self.assertAlmostEqual(background['sigma']*1e8, 1.)
        self.assertEqual(background['indices'][0], True)
        self.assertEqual(background['indices'][1:].all(), False)

        # similar, but now increasing exponentially
        lc.reset()
        lc.fluxes = numpy.logspace(-6, -4, 30)
        background = lc.calc_background()
        self.assertAlmostEqual(background['mean']*1e6, 1.0)
        self.assertAlmostEqual(background['sigma']*1e8, 1.0)
        self.assertEqual(background['indices'][0], True)
        self.assertEqual(background['indices'][1:].any(), False)


    def test_calc_duration(self):
        lc = self.lightcurve
        lc.reset()

        duration = lc.calc_duration()
        self.assertTrue(numpy.isnan(duration['start']))
        self.assertTrue(numpy.isnan(duration['end']))
        self.assertEqual(duration['total'], 0.)
        self.assertEqual(duration['active'], 0.)

        # Corner cases first
        # transient at start
        lc.reset()
        lc.fluxes[0] *= 4.
        duration = lc.calc_duration()
        self.assertEqual(duration['start'], DateTime(2010, 10, 1, 12, 0, 0, 0, 30.0))
        self.assertEqual(duration['end'], DateTime(2010, 10, 1, 12, 0, 0, 0, 30.0))
        self.assertAlmostEqual(duration['total'], 60.0)
        self.assertAlmostEqual(duration['active'], 60.0)

        # transient on first two light curve points
        lc.reset()
        lc.fluxes[1] *= 2.
        duration = lc.calc_duration()
        self.assertEqual(duration['start'], DateTime(2010, 10, 1, 12, 0, 0, 0, 30.0))
        self.assertEqual(duration['end'], DateTime(2010, 10, 1, 12, 1, 0, 0, 30.0))
        self.assertAlmostEqual(duration['total'], 60.0)
        self.assertAlmostEqual(duration['active'], 120.0)

        # transient near very end
        lc.reset()
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 4.
        duration = lc.calc_duration()
        self.assertEqual(duration['start'], DateTime(2010, 10, 1, 12, 29, 0, 0, 30.0))
        self.assertEqual(duration['end'], DateTime(2010, 10, 1, 12, 29, 0, 0, 30.0))
        self.assertAlmostEqual(duration['total'], 60.)
        self.assertAlmostEqual(duration['active'], 60.)

        # transient at last two light curve points
        lc.reset()
        lc.fluxes[-2] *= 2.
        duration = lc.calc_duration()
        self.assertEqual(duration['start'], DateTime(2010, 10, 1, 12, 28, 0, 0, 30.0))
        self.assertEqual(duration['end'], DateTime(2010, 10, 1, 12, 29, 0, 0, 30.0))
        self.assertAlmostEqual(duration['total'], 60.)
        self.assertAlmostEqual(duration['active'], 120.)

        # single peak transient
        # transient at last two light curve points
        lc.reset()
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 4.
        duration = lc.calc_duration()
        self.assertEqual(duration['start'], DateTime(2010, 10, 1, 12, 6, 0, 0, 30.0))
        self.assertEqual(duration['end'], DateTime(2010, 10, 1, 12, 6, 0, 0, 30.0))
        self.assertAlmostEqual(duration['total'], 60.)
        self.assertAlmostEqual(duration['active'], 60.)

        # longer transient
        lc.reset()
        lc.fluxes[5] *= 2.
        lc.fluxes[7] *= 2.
        duration = lc.calc_duration()
        self.assertEqual(duration['start'], DateTime(2010, 10, 1, 12, 5, 0, 0, 30.0))
        self.assertEqual(duration['end'], DateTime(2010, 10, 1, 12, 7, 0, 0, 30.0))
        self.assertAlmostEqual(duration['total'], 120.)
        self.assertAlmostEqual(duration['active'], 180.)

        # Double peaked transient
        lc.reset()
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 4.
        duration = lc.calc_duration()
        self.assertEqual(duration['start'], DateTime(2010, 10, 1, 12, 5, 0, 0, 30.0))
        self.assertEqual(duration['end'], DateTime(2010, 10, 1, 12, 17, 0, 0, 30.0))
        self.assertAlmostEqual(duration['total'], 720.)
        self.assertAlmostEqual(duration['active'], 360.)


    def test_calc_fluxincrease(self):
        lc = self.lightcurve
        lc.reset()

        fluxincrease = lc.calc_fluxincrease()
        self.assertTrue(numpy.isnan(fluxincrease['peak']))
        self.assertTrue(numpy.isnan(fluxincrease['increase']['absolute']))
        self.assertTrue(numpy.isnan(fluxincrease['increase']['relative']))
        self.assertEqual(fluxincrease['ipeak'], None)

        lc.reset()
        lc.fluxes[0] *= 2.
        fluxincrease = lc.calc_fluxincrease()
        self.assertAlmostEqual(fluxincrease['peak']*1e6, 2.01)
        self.assertAlmostEqual(fluxincrease['increase']['relative'], 2.010346611)
        self.assertAlmostEqual(fluxincrease['increase']['absolute']*1e6, 1.010172414)
        self.assertEqual(fluxincrease['ipeak'], 0)

        lc.reset()
        lc.fluxes[0] *= 2.
        lc.fluxes[1] *= 2.
        fluxincrease = lc.calc_fluxincrease()
        self.assertAlmostEqual(fluxincrease['peak']*1e6, 4.02)
        self.assertAlmostEqual(fluxincrease['increase']['relative'], 4.02)
        self.assertAlmostEqual(fluxincrease['increase']['absolute']*1e6, 3.02)
        self.assertEqual(fluxincrease['ipeak'], 0)

        lc.reset()
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 2.
        fluxincrease = lc.calc_fluxincrease()
        self.assertAlmostEqual(fluxincrease['peak']*1e6, 1.98)
        self.assertAlmostEqual(fluxincrease['increase']['relative'], 1.979317477)
        self.assertAlmostEqual(fluxincrease['increase']['absolute']*1e7, 9.796551724)
        self.assertEqual(fluxincrease['ipeak'], 29)

        lc.reset()
        lc.fluxes[-1] *= 2.
        lc.fluxes[-2] *= 2.
        fluxincrease = lc.calc_fluxincrease()
        self.assertAlmostEqual(fluxincrease['peak']*1e6, 3.96)
        self.assertAlmostEqual(fluxincrease['increase']['relative'], 3.96)
        self.assertAlmostEqual(fluxincrease['increase']['absolute']*1e6, 2.96)
        self.assertEqual(fluxincrease['ipeak'], 29)

        lc.reset()
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 2.
        fluxincrease = lc.calc_fluxincrease()
        self.assertAlmostEqual(fluxincrease['peak']*1e6, 2.016)
        self.assertAlmostEqual(fluxincrease['increase']['relative'], 2.016556291390)
        self.assertAlmostEqual(fluxincrease['increase']['absolute']*1e6, 1.0162758620)
        self.assertEqual(fluxincrease['ipeak'], 6)

        lc.reset()
        lc.fluxes[5] *= 2.
        lc.fluxes[6] *= 2.
        lc.fluxes[7] *= 2.
        fluxincrease = lc.calc_fluxincrease()
        self.assertAlmostEqual(fluxincrease['peak']*1e6, 4.032)
        self.assertAlmostEqual(fluxincrease['increase']['relative'], 4.03125347)
        self.assertAlmostEqual(fluxincrease['increase']['absolute']*1e6, 3.0318148148)
        self.assertEqual(fluxincrease['ipeak'], 6)

        lc.reset()
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 8.
        lc.fluxes[18] *= 4.
        fluxincrease = lc.calc_fluxincrease()
        self.assertAlmostEqual(fluxincrease['peak']*1e6, 8.2)
        self.assertAlmostEqual(fluxincrease['increase']['relative'], 8.19821777874)
        self.assertAlmostEqual(fluxincrease['increase']['absolute']*1e6, 7.1997826086)
        self.assertEqual(fluxincrease['ipeak'], 16)

    def test_calc_risefall(self):
        lc = self.lightcurve
        lc.reset()

        risefall = lc.calc_risefall()
        self.assertTrue(numpy.isnan(risefall['rise']['flux']))
        self.assertTrue(numpy.isnan(risefall['rise']['time']))
        self.assertTrue(numpy.isnan(risefall['fall']['flux']))
        self.assertTrue(numpy.isnan(risefall['fall']['time']))
        self.assertTrue(numpy.isnan(risefall['ratio']))

        lc.reset()
        lc.fluxes[0] *= 2.
        risefall = lc.calc_risefall()
        self.assertAlmostEqual(risefall['rise']['time'], 0.0)
        self.assertAlmostEqual(risefall['rise']['flux']*1e6, 1.01017241)
        self.assertAlmostEqual(risefall['fall']['time'], 60.0)
        self.assertAlmostEqual(risefall['fall']['flux']*1e6, 1.01017241)
        self.assertTrue(numpy.isnan(risefall['ratio']))

        lc.reset()
        lc.fluxes[0] *= 2.
        lc.fluxes[1] *= 2.
        risefall = lc.calc_risefall()
        self.assertAlmostEqual(risefall['rise']['time'], 0.0)
        self.assertAlmostEqual(risefall['rise']['flux']*1e6, 3.02)
        self.assertAlmostEqual(risefall['fall']['time'], 120.0)
        self.assertAlmostEqual(risefall['fall']['flux']*1e6, 3.02)
        self.assertTrue(numpy.isnan(risefall['ratio']))

        lc.reset()
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 2.
        risefall = lc.calc_risefall()
        self.assertAlmostEqual(risefall['rise']['time'], 60.0)
        self.assertAlmostEqual(risefall['rise']['flux']*1e7, 9.7965517)
        self.assertAlmostEqual(risefall['fall']['time'], 0.)
        self.assertAlmostEqual(risefall['fall']['flux']*1e7, 9.7965517)
        self.assertTrue(numpy.isnan(risefall['ratio']))

        lc.reset()
        lc.fluxes[-1] *= 2.
        lc.fluxes[-2] *= 2.
        risefall = lc.calc_risefall()
        self.assertAlmostEqual(risefall['rise']['time'], 120.0)
        self.assertAlmostEqual(risefall['rise']['flux']*1e6, 2.96)
        self.assertAlmostEqual(risefall['fall']['time'], 0.0)
        self.assertAlmostEqual(risefall['fall']['flux']*1e6, 2.96)
        self.assertTrue(numpy.isnan(risefall['ratio']))

        lc.reset()
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 2.
        risefall = lc.calc_risefall()
        self.assertAlmostEqual(risefall['rise']['time'], 60.0)
        self.assertAlmostEqual(risefall['rise']['flux']*1e6, 1.01627586)
        self.assertAlmostEqual(risefall['fall']['time'], 60.0)
        self.assertAlmostEqual(risefall['fall']['flux']*1e6, 1.01627586)
        self.assertAlmostEqual(risefall['ratio'], 1.0)

        lc.reset()
        lc.fluxes[5] *= 2.
        lc.fluxes[6] *= 2.
        lc.fluxes[7] *= 2.
        risefall = lc.calc_risefall()
        self.assertAlmostEqual(risefall['rise']['time'], 120.0)
        self.assertAlmostEqual(risefall['rise']['flux']*1e6, 3.0318148)
        self.assertAlmostEqual(risefall['fall']['time'], 120.0)
        self.assertAlmostEqual(risefall['fall']['flux']*1e6, 3.0318148)
        self.assertAlmostEqual(risefall['ratio'], 1.0)

        lc.reset()
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 8.
        lc.fluxes[18] *= 4.
        risefall = lc.calc_risefall()
        self.assertAlmostEqual(risefall['rise']['time'], 120.0)
        self.assertAlmostEqual(risefall['rise']['flux']*1e6, 7.1997826)
        self.assertAlmostEqual(risefall['fall']['time'], 180.0)
        self.assertAlmostEqual(risefall['fall']['flux']*1e6, 7.1997826)
        self.assertAlmostEqual(risefall['ratio'], 1.5)

        # Test bug fix that caused incorrect background indices to be calculated
        # when at the end of the background calculation, the indices were not
        # recalculated using the actual estimated background.
        lc = lcmod.LightCurve(
            taustart_tss=numpy.array([self.timezero + timedelta(0, s) for s in
                      numpy.arange(0, 7*60, 60, dtype=numpy.float)]),
            tau_times=numpy.ones(7, dtype=numpy.float) * 60,
            fluxes=numpy.array([90., 50., 40., 90., 70., 50., 70.]),
            errors=numpy.array([6., 6., 7., 5., 6., 3., 5.]),
            srcids=numpy.arange(0, 7)
        )
        lc.reset()
        risefall = lc.calc_risefall()
        self.assertTrue(numpy.isnan(risefall['rise']['flux']))
        self.assertTrue(numpy.isnan(risefall['rise']['time']))
        self.assertTrue(numpy.isnan(risefall['fall']['flux']))
        self.assertTrue(numpy.isnan(risefall['fall']['time']))
        self.assertTrue(numpy.isnan(risefall['ratio']))


class TestLightcurves(unittest.TestCase):
    """Test a variety of light curves, some more or less pathological"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constant(self):
        """Constant light curve"""

        npoints = 60  # number of datapoints
        tau_time = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            taustart_tss=numpy.array([timezero + timedelta(0, s) for s in
                      numpy.arange(0, npoints*tau_time, tau_time, dtype=numpy.float)]),
            tau_times=numpy.ones(npoints, dtype=numpy.float) * tau_time,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            srcids=numpy.arange(0, npoints)
        )
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.)
        self.assertAlmostEqual(stats['wstddev'], 0.)
        self.assertTrue(numpy.isnan(stats['wskew']))
        self.assertTrue(numpy.isnan(stats['wkurtosis']))

    def test_gauss(self):
        """Gaussian shaped light curves

        + Shallow and spiked

        + With  or without extended background.
        """

        npoints = 60  # number of datapoints
        tau_time = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            taustart_tss=numpy.array([timezero + timedelta(0, s) for s in
                      numpy.arange(0, npoints*tau_time, tau_time, dtype=numpy.float)]),
            tau_times=numpy.ones(npoints, dtype=numpy.float) * tau_time,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            srcids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6

        # narrow
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/3.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean'], 1.051166e-6)
        self.assertAlmostEqual(stats['wstddev'], 1.847346e-7)
        self.assertAlmostEqual(stats['wskew'], 3.8471315)
        self.assertAlmostEqual(stats['wkurtosis'], 14.2676929)

        # average
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.1477044876)
        self.assertAlmostEqual(stats['wstddev']*1e7, 2.8987354775)
        self.assertAlmostEqual(stats['wskew'], 1.86565726033)
        self.assertAlmostEqual(stats['wkurtosis'], 2.05809248174)

        # broad
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/150.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.36160539869)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.566410425)
        self.assertAlmostEqual(stats['wskew'], 0.571435391624)
        self.assertAlmostEqual(stats['wkurtosis'], -1.257947575)

    def test_double_peaked(self):
        """Double peaked light curves

        + Shallow and spiked

        + Equal and unequal peaks
        """

        npoints = 60  # number of datapoints
        tau_time = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            taustart_tss=numpy.array([timezero + timedelta(0, s) for s in
                      numpy.arange(0, npoints*tau_time, tau_time, dtype=numpy.float)]),
            tau_times=numpy.ones(npoints, dtype=numpy.float) * tau_time,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            srcids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6

        # Two equal Gaussian peaks, next to each other
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+20)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-20)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.2946776227)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.5229426977)
        self.assertAlmostEqual(stats['wskew'], 0.847967059)
        self.assertAlmostEqual(stats['wkurtosis'], -0.8656540569)

        # Two equal Gaussian peaks, slightly overlapping
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+10)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-10)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.295408972)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.517837865)
        self.assertAlmostEqual(stats['wskew'], 0.8485974673)
        self.assertAlmostEqual(stats['wkurtosis'], -0.863237211)

        # Two equal Gaussian peaks, largely overlapping
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+5)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-5)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.295408975)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.90421976)
        self.assertAlmostEqual(stats['wskew'], 0.7980233823)
        self.assertAlmostEqual(stats['wkurtosis'], -1.14843900)

        # Two equal peaks on the edges of the light curve
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+25)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-25)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.2717658775)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.635655425)
        self.assertAlmostEqual(stats['wskew'], 0.89747190057)
        self.assertAlmostEqual(stats['wkurtosis'], -0.86263231)


        # Two unequal Gaussian peaks, next to each other
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+20)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-20)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.1586310125)
        self.assertAlmostEqual(stats['wstddev']*1e7, 2.573732986)
        self.assertAlmostEqual(stats['wskew'], 1.9572166)
        self.assertAlmostEqual(stats['wkurtosis'], 2.96265432)

        # Two unequal Gaussian peaks, slightly overlapping
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+10)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-10)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.15872275)
        self.assertAlmostEqual(stats['wstddev']*1e7, 2.573209197)
        self.assertAlmostEqual(stats['wskew'], 1.957711629)
        self.assertAlmostEqual(stats['wkurtosis'], 2.964457311)

        # Two unequal Gaussian peaks, largely overlapping
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+5)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-5)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.15872275)
        self.assertAlmostEqual(stats['wstddev']*1e7, 2.65973335)
        self.assertAlmostEqual(stats['wskew'], 1.84573887)
        self.assertAlmostEqual(stats['wkurtosis'], 2.4994102)

        # Two unequal peaks on the edges of the light curve
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+25)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-25)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.150463628)
        self.assertAlmostEqual(stats['wstddev']*1e7, 2.60591588)
        self.assertAlmostEqual(stats['wskew'], 1.9595226)
        self.assertAlmostEqual(stats['wkurtosis'], 2.926038515)

        # Three unequal Gaussian peaks, next to each other
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+20)**2)/25.)
        gauss += 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float))**2)/5.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-20)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.178447649)
        self.assertAlmostEqual(stats['wstddev']*1e7, 2.5243424)
        self.assertAlmostEqual(stats['wskew'], 1.87494360)
        self.assertAlmostEqual(stats['wkurtosis'], 2.80140004)

        # Three unequal Gaussian peaks, overlapping
        gauss = 0.4*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+6)**2)/5.)
        gauss += 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-8)**2)/3.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float))**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.18947657)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.13672913)
        self.assertAlmostEqual(stats['wskew'], 1.37923736)
        self.assertAlmostEqual(stats['wkurtosis'], 0.40229112)

        # Three unequal Gaussian peaks, overlapping, but shifted compared to previous
        gauss = 0.4*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+11)**2)/5.)
        gauss += 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-3)**2)/3.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+5)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 1.18947657)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.13672913)
        self.assertAlmostEqual(stats['wskew'], 1.37923736)
        self.assertAlmostEqual(stats['wkurtosis'], 0.40229112)


    def test_constant_derivative(self):
        """Light curves with an unchanging derivate"""

        npoints = 60  # number of datapoints
        tau_time = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            taustart_tss=numpy.array([timezero + timedelta(0, s) for s in
                      numpy.arange(0, npoints*tau_time, tau_time, dtype=numpy.float)]),
            tau_times=numpy.ones(npoints, dtype=numpy.float) * tau_time,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            srcids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6
        change = numpy.linspace(1, 10, num=fluxes.shape[0])

        # Linear increase
        lightcurve.fluxes = fluxes * change
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 5.5)
        self.assertAlmostEqual(stats['wstddev']*1e6, 2.664038013)
        self.assertAlmostEqual(stats['wskew'], 0.)
        self.assertAlmostEqual(stats['wkurtosis'], -1.26014481)

        # Linear decrease
        lightcurve.fluxes = fluxes * change[::-1]
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e6, 5.5)
        self.assertAlmostEqual(stats['wstddev']*1e6, 2.664038013)
        self.assertAlmostEqual(stats['wskew'], 0.)
        self.assertAlmostEqual(stats['wkurtosis'], -1.26014481)

        # Quadratic increase
        lightcurve.fluxes = fluxes * change * change
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e5, 3.722881356)
        self.assertAlmostEqual(stats['wstddev']*1e5, 2.997230982)
        self.assertAlmostEqual(stats['wskew'], 0.530594134)
        self.assertAlmostEqual(stats['wkurtosis'], -1.0226088379)

        # Quadratic decrease
        lightcurve.fluxes = fluxes * change[::-1] * change[::-1]
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e5, 3.722881356)
        self.assertAlmostEqual(stats['wstddev']*1e5, 2.997230982)
        self.assertAlmostEqual(stats['wskew'], 0.530594134)
        self.assertAlmostEqual(stats['wkurtosis'], -1.0226088379)

        # Exponential increase
        lightcurve.fluxes = fluxes * numpy.exp(change)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean'], 0.002594539)
        self.assertAlmostEqual(stats['wstddev'], 0.0049424894)
        self.assertAlmostEqual(stats['wskew'], 2.3239532572)
        self.assertAlmostEqual(stats['wkurtosis'], 4.812191265)

        # Exponential decrease
        lightcurve.fluxes = fluxes * numpy.exp(change[::-1])
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean'], 0.002594539)
        self.assertAlmostEqual(stats['wstddev'], 0.0049424894)
        self.assertAlmostEqual(stats['wskew'], 2.3239532572)
        self.assertAlmostEqual(stats['wkurtosis'], 4.812191265)

        maximum = max(numpy.exp(change))
        # Inverse exponential increase
        lightcurve.fluxes = fluxes * (maximum - numpy.exp(change) + 1)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean'], 0.0194329267)
        self.assertAlmostEqual(stats['wstddev'], 0.0049424894)
        self.assertAlmostEqual(stats['wskew'], -2.323953257)
        self.assertAlmostEqual(stats['wkurtosis'], 4.812191265)

        # Inverse exponential decrease
        lightcurve.fluxes = fluxes * (maximum - numpy.exp(change[::-1]) + 1)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean'], 0.0194329267)
        self.assertAlmostEqual(stats['wstddev'], 0.0049424894)
        self.assertAlmostEqual(stats['wskew'], -2.323953257)
        self.assertAlmostEqual(stats['wkurtosis'], 4.812191265)

    def test_dipping(self):
        """Light curves dropping below background"""

        npoints = 60  # number of datapoints
        tau_time = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            taustart_tss=numpy.array([timezero + timedelta(0, s) for s in
                      numpy.arange(0, npoints*tau_time, tau_time, dtype=numpy.float)]),
            tau_times=numpy.ones(npoints, dtype=numpy.float) * tau_time,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            srcids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6
        change = numpy.linspace(1, 10, num=fluxes.shape[0])
        lightcurve.fluxes = fluxes
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/3.)
        lightcurve.fluxes = fluxes * (1 - gauss)
        stats = lightcurve.calc_stats()
        self.assertAlmostEqual(stats['wmean']*1e7, 9.488336646)
        self.assertAlmostEqual(stats['wstddev']*1e7, 1.8474562)
        self.assertAlmostEqual(stats['wskew'], -3.84713153)
        self.assertAlmostEqual(stats['wkurtosis'], 14.2676929)
        # Get the stats, but this time without the background section
        lightcurve.calc_background()
        stats = lightcurve.calc_stats(-lightcurve.background['indices'])
        self.assertAlmostEqual(stats['wmean']*1e7, 5.628812808)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.72659188)
        self.assertAlmostEqual(stats['wskew'], -0.263062962)
        self.assertAlmostEqual(stats['wkurtosis'], -1.8192641814)


        # Increasing the number of points gives a better background estimate,
        npoints = 180  # number of datapoints
        tau_time = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            taustart_tss=numpy.array([timezero + timedelta(0, s) for s in
                      numpy.arange(0, npoints*tau_time, tau_time,
                                   dtype=numpy.float)]),
            tau_times=numpy.ones(npoints, dtype=numpy.float) * tau_time,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            srcids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6
        change = numpy.linspace(1, 10, num=fluxes.shape[0])
        lightcurve.fluxes = fluxes
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2,
                                         dtype=numpy.float)**2)/3.)
        lightcurve.fluxes = fluxes * (1 - gauss)
        stats = lightcurve.calc_stats()
        # Note how the statistics change when more background data is available,
        self.assertAlmostEqual(stats['wmean']*1e7, 9.82944555)
        self.assertAlmostEqual(stats['wstddev']*1e7, 1.087882855)
        self.assertAlmostEqual(stats['wskew'], -7.17736487336)
        self.assertAlmostEqual(stats['wkurtosis'], 53.3102313227)
        # Get the stats, but this time without the background section
        # Now, the statistics are the same as previously, even with
        # more background data
        lightcurve.calc_background()
        stats = lightcurve.calc_stats(-lightcurve.background['indices'])
        self.assertAlmostEqual(stats['wmean']*1e7, 5.628812808)
        self.assertAlmostEqual(stats['wstddev']*1e7, 3.72659188)
        self.assertAlmostEqual(stats['wskew'], -0.263062962)
        self.assertAlmostEqual(stats['wkurtosis'], -1.8192641814)

    def test_periodic(self):
        """Various periodic light curves"""

        pass


if __name__ == '__main__':
    unittest.main()
