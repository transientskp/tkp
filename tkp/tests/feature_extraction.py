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


import sys
import os
import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
from optparse import OptionParser
from datetime import datetime
from datetime import timedelta
import logging
import math
import numpy
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from tkp.classification.features import lightcurve as lcmod
from tkp.classification.manual.utils import DateTime


# Set this variable if you want to see what the light curves look like
ENABLE_PLOTTING = True


class TestLightcurve(unittest.TestCase):
    """  """

    def setUp(self):
        # create test data
        self.timezero = datetime(2010, 10, 1, 12, 0, 0)
        self.lightcurve = lcmod.LightCurve(
            obstimes=numpy.array([self.timezero + timedelta(0, s) for s in 
                      numpy.arange(0, 30*60, 60, dtype=numpy.float)]),
            inttimes=numpy.ones(30, dtype=numpy.float) * 60,
            fluxes=numpy.ones(30, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(30, dtype=numpy.float) * 1e-8,
            sourceids=numpy.arange(0, 30)
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
        logger = logging.getLogger('tkp')

        lc = self.lightcurve
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient1.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.)
        self.assertAlmostEqual(sigma*1e8, 1.14138451921)
        self.assertEqual(indices.all(), True)

        # Corner cases first
        # transient at start
        lc.fluxes[0] *= 4.
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient2.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 0.999827586)
        self.assertAlmostEqual(sigma*1e8, 1.1576049676)
        self.assertEqual(indices[0], False)
        self.assertEqual(indices[1:].all(), True)

        # transient on first two light curve points
        lc.fluxes[1] *= 2.
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient3.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.)
        self.assertAlmostEqual(sigma*1e8, 1.17504925035)
        self.assertEqual(indices[2:].all(), True)
        self.assertEqual(indices[0:2].any(), False)

        # transient near very end
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 4.
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient4.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.0003448276)
        self.assertAlmostEqual(sigma*1e8, 1.145574049)
        self.assertEqual(indices[:-1].all(), True)
        self.assertEqual(indices[-1], False)

        # transient at last two light curve points
        lc.fluxes[-2] *= 2.
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient5.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.)
        self.assertAlmostEqual(sigma*1e8, 1.1511668798)
        self.assertEqual(indices[:-2].all(), True)
        self.assertEqual(indices[-2:].any(), False)

        # single peak transient
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 4.
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient6.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 0.9997241379)
        self.assertAlmostEqual(sigma*1e8, 1.151364579)
        self.assertEqual(indices[6], False)
        self.assertEqual(indices[:6].all(), True)
        self.assertEqual(indices[7:].all(), True)

        # longer transient
        lc.fluxes[5] *= 2.
        lc.fluxes[7] *= 2.
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient7.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.000185185)
        self.assertAlmostEqual(sigma*1e8, 1.18062468)
        self.assertEqual(indices[:5].all(), True)
        self.assertEqual(indices[8:].all(), True)
        self.assertEqual(indices[5:8].any(), False)

        # Double peaked transient        
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 4.
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient8.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.000416667)
        self.assertAlmostEqual(sigma*1e8, 1.009914618)
        self.assertEqual(indices[:5].all(), True)
        self.assertEqual(indices[8:15].all(), True)
        self.assertEqual(indices[18:].all(), True)
        self.assertEqual(indices[5:8].any(), False)
        self.assertEqual(indices[15:18].any(), False)

        # steadily increasing background
        lc.fluxes = numpy.linspace(1.e-6, 1.e-4, 30)
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient11.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.)
        self.assertAlmostEqual(sigma*1e8, 1.)
        self.assertEqual(indices[0], True)
        self.assertEqual(indices[1:].all(), False)

        # similar, but now increasing exponentially
        lc.fluxes = numpy.logspace(-6, -4, 30)
        mean, sigma, indices = lcmod.calc_background(
            lc)
        plot_lightcurve(lc, "transient12.png", (mean, sigma, indices))
        self.assertAlmostEqual(mean*1e6, 1.0)
        self.assertAlmostEqual(sigma*1e8, 1.0)
        self.assertEqual(indices[0], True)
        self.assertEqual(indices[1:].any(), False)
        

    def test_calc_duration(self):
        lc = self.lightcurve
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, None)
        self.assertEqual(tend, None)
        self.assertEqual(duration, None)
        self.assertEqual(active, None)
        
        # Corner cases first
        # transient at start
        lc.fluxes[0] *= 4.
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 0, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 0, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 0.0)
        self.assertAlmostEqual(active, 60.0)
        
        # transient on first two light curve points
        lc.fluxes[1] *= 2.
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 0, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 1, 0, 0, 30.0))        
        self.assertAlmostEqual(duration, 60.0)
        self.assertAlmostEqual(active, 120.0)

        # transient near very end
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 4.
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 29, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 29, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 0.)
        self.assertAlmostEqual(active, 60.)
        
        # transient at last two light curve points
        lc.fluxes[-2] *= 2.
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 28, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 29, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 60.)
        self.assertAlmostEqual(active, 120.)

        # single peak transient
        # transient at last two light curve points
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 4.
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 6, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 6, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 0.)
        self.assertAlmostEqual(active, 60.)

        # longer transient
        lc.fluxes[5] *= 2.
        lc.fluxes[7] *= 2.
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 5, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 7, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 120.)
        self.assertAlmostEqual(active, 180.)

        # Double peaked transient
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 4.
        tzero, tend, duration, active = lcmod.calc_duration(lc)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 5, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 17, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 720.)
        self.assertAlmostEqual(active, 360.)
        

    def test_calc_fluxincrease(self):
        lc = self.lightcurve
        background = {'mean': 1.0e-6, 'sigma': 1.0e-8}
        indices = numpy.ones(30, dtype=numpy.bool)

        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 0.0)
        self.assertEqual(increase, {})
        self.assertEqual(ipeak, None)

        indices[0] = False
        lc.fluxes[0] *= 2.
        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux*1e6, 2.01)
        self.assertAlmostEqual(increase['percent'], 2.01)
        self.assertAlmostEqual(increase['absolute']*1e6, 1.01)
        self.assertEqual(ipeak, 0)

        indices[1] = False
        lc.fluxes[0] *= 2.
        lc.fluxes[1] *= 2.
        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux*1e6, 4.02)
        self.assertAlmostEqual(increase['percent'], 4.02)
        self.assertAlmostEqual(increase['absolute']*1e6, 3.02)
        self.assertEqual(ipeak, 0)

        indices[0] = indices[1] = True
        indices[-1] = False
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 2.
        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux*1e6, 1.98)
        self.assertAlmostEqual(increase['percent'], 1.98)
        self.assertAlmostEqual(increase['absolute']*1e7, 9.8)
        self.assertEqual(ipeak, 29)

        indices[-2] = False
        lc.fluxes[-1] *= 2.
        lc.fluxes[-2] *= 2.
        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux*1e6, 3.96)
        self.assertAlmostEqual(increase['percent'], 3.96)
        self.assertAlmostEqual(increase['absolute']*1e6, 2.96)
        self.assertEqual(ipeak, 29)

        indices[-2] = indices[-1] = True
        indices[6] = False
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 2.
        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux*1e6, 2.016)
        self.assertAlmostEqual(increase['percent'], 2.016)
        self.assertAlmostEqual(increase['absolute']*1e6, 1.016)
        self.assertEqual(ipeak, 6)

        indices[5] = indices[7] = False
        lc.fluxes[5] *= 2.
        lc.fluxes[6] *= 2.
        lc.fluxes[7] *= 2.
        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux*1e6, 4.032)
        self.assertAlmostEqual(increase['percent'], 4.032)
        self.assertAlmostEqual(increase['absolute']*1e6, 3.032)
        self.assertEqual(ipeak, 6)

        indices[15] = indices[16] = indices[17] = indices[18] = False
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 8.
        lc.fluxes[18] *= 4.
        peakflux, increase, ipeak = lcmod.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux*1e6, 8.2)
        self.assertAlmostEqual(increase['percent'], 8.2)
        self.assertAlmostEqual(increase['absolute']*1e6, 7.2)
        self.assertEqual(ipeak, 16)

    def test_calc_risefall(self):
        lc = self.lightcurve
        background = {'mean': 1.0e-6, 'sigma': 1.0e-8}
        indices = numpy.ones(30, dtype=numpy.bool)

        ipeak = None
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        # all zeroes are integers!
        self.assertEqual(rise['time'], 0)
        self.assertEqual(rise['flux'], 0)
        self.assertEqual(fall['time'], 0)
        self.assertEqual(fall['flux'], 0)
        self.assertEqual(ratio, 0)

        ipeak = 0
        indices[0] = False
        lc.fluxes[0] *= 2.
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertEqual(rise['time'], 0)  # integer!
        self.assertAlmostEqual(rise['flux']*1e6, 1.01)
        self.assertAlmostEqual(fall['time'], 60.0)
        self.assertAlmostEqual(fall['flux']*1e6, 1.01)
        self.assertEqual(ratio, 0)  # integer!

        indices[1] = False
        lc.fluxes[0] *= 2.
        lc.fluxes[1] *= 2.
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertEqual(rise['time'], 0)  # integer!
        self.assertAlmostEqual(rise['flux']*1e6, 3.02)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux']*1e6, 3.02)
        self.assertEqual(ratio, 0)  # integer!

        ipeak = 29
        indices[0] = indices[1] = True
        indices[-1] = False
        lc.fluxes[0] /= 4.
        lc.fluxes[1] /= 2.
        lc.fluxes[-1] *= 2.
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 60.0)
        self.assertAlmostEqual(rise['flux']*1e7, 9.8)
        self.assertEqual(fall['time'], 0)  # integer!
        self.assertAlmostEqual(fall['flux']*1e7, 9.8)
        self.assertEqual(ratio, 0)

        indices[-2] = False
        lc.fluxes[-1] *= 2.
        lc.fluxes[-2] *= 2.
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 120.0)
        self.assertAlmostEqual(rise['flux']*1e6, 2.96)
        self.assertEqual(fall['time'], 0)  # integer!
        self.assertAlmostEqual(fall['flux']*1e6, 2.96)
        self.assertEqual(ratio, 0)

        ipeak = 6
        indices[-2] = indices[-1] = True
        indices[6] = False
        lc.fluxes[-1] /= 4.
        lc.fluxes[-2] /= 2.
        lc.fluxes[6] *= 2.
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 60.0)
        self.assertAlmostEqual(rise['flux']*1e6, 1.016)
        self.assertAlmostEqual(fall['time'], 60.0)
        self.assertAlmostEqual(fall['flux']*1e6, 1.016)
        self.assertAlmostEqual(ratio, 1.0)


        indices[5] = indices[7] = False
        lc.fluxes[5] *= 2.
        lc.fluxes[6] *= 2.
        lc.fluxes[7] *= 2.
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 120.0)
        self.assertAlmostEqual(rise['flux']*1e6, 3.032)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux']*1e6, 3.032)
        self.assertAlmostEqual(ratio, 1.0)

        ipeak = 16
        indices[15] = indices[16] = indices[17] = False
        lc.fluxes[15] *= 4.
        lc.fluxes[16] *= 8.
        lc.fluxes[17] *= 8.
        lc.fluxes[18] *= 4.
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 120.0)
        self.assertAlmostEqual(rise['flux']*1e6, 7.2)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux']*1e6, 7.2)
        self.assertAlmostEqual(ratio, 1.0)

        # Change the duration of the second event by shifting the peak
        # so that the rise and fall ratio != 1
        # Note: normally, we'd need extra data for the background to
        # obtain correct results, as demonstrated above; in this case
        # we have manually set indices to be correct.
        lc.fluxes[17] *= 2.
        lc.fluxes[18] *= 2.
        indices[18] = False
        ipeak = 17
        rise, fall, ratio = lcmod.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 180.0)
        self.assertAlmostEqual(rise['flux']*1e5, 1.46)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux']*1e5, 1.46)
        self.assertAlmostEqual(ratio, 2/3.)
        

class TestLightcurves(unittest.TestCase):
    """Test a variety of light curves, some more or less pathological"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constant(self):
        """Constant light curve"""

        npoints = 60  # number of datapoints
        inttime = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            obstimes=numpy.array([timezero + timedelta(0, s) for s in 
                      numpy.arange(0, npoints*inttime, inttime, dtype=numpy.float)]),
            inttimes=numpy.ones(npoints, dtype=numpy.float) * inttime,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            sourceids=numpy.arange(0, npoints)
        )
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant1.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.)
        self.assertAlmostEqual(stats['stddev'], 0.)
        self.assertEqual(str(stats['skew']), "nan")
        self.assertEqual(str(stats['kurtosis']), "nan")
    
    def test_gauss(self):
        """Gaussian shaped light curves

        + Shallow and spiked

        + With  or without extended background.
        """

        npoints = 60  # number of datapoints
        inttime = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            obstimes=numpy.array([timezero + timedelta(0, s) for s in 
                      numpy.arange(0, npoints*inttime, inttime, dtype=numpy.float)]),
            inttimes=numpy.ones(npoints, dtype=numpy.float) * inttime,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            sourceids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6

        # narrow
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/3.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "gauss1.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean'], 1.051166e-6)
        self.assertAlmostEqual(stats['stddev'], 1.847346e-7)
        self.assertAlmostEqual(stats['skew'], 3.8471315)
        self.assertAlmostEqual(stats['kurtosis'], 14.2676929)

        # average
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "gauss2.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.1477044876)
        self.assertAlmostEqual(stats['stddev']*1e7, 2.8987354775)
        self.assertAlmostEqual(stats['skew'], 1.86565726033)
        self.assertAlmostEqual(stats['kurtosis'], 2.05809248174)

        # broad
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/150.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "gauss3.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.36160539869)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.566410425)
        self.assertAlmostEqual(stats['skew'], 0.571435391624)
        self.assertAlmostEqual(stats['kurtosis'], -1.257947575)

    def test_double_peaked(self):
        """Double peaked light curves

        + Shallow and spiked

        + Equal and unequal peaks
        """

        npoints = 60  # number of datapoints
        inttime = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            obstimes=numpy.array([timezero + timedelta(0, s) for s in 
                      numpy.arange(0, npoints*inttime, inttime, dtype=numpy.float)]),
            inttimes=numpy.ones(npoints, dtype=numpy.float) * inttime,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            sourceids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6
        
        # Two equal Gaussian peaks, next to each other
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+20)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-20)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double1.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.2946776227)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.5229426977)
        self.assertAlmostEqual(stats['skew'], 0.847967059)
        self.assertAlmostEqual(stats['kurtosis'], -0.8656540569)

        # Two equal Gaussian peaks, slightly overlapping
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+10)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-10)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double2.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.295408972)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.517837865)
        self.assertAlmostEqual(stats['skew'], 0.8485974673)
        self.assertAlmostEqual(stats['kurtosis'], -0.863237211)

        # Two equal Gaussian peaks, largely overlapping
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+5)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-5)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double3.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.295408975)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.90421976)
        self.assertAlmostEqual(stats['skew'], 0.7980233823)
        self.assertAlmostEqual(stats['kurtosis'], -1.14843900)

        # Two equal peaks on the edges of the light curve
        gauss = numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+25)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-25)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double4.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.2717658775)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.635655425)
        self.assertAlmostEqual(stats['skew'], 0.89747190057)
        self.assertAlmostEqual(stats['kurtosis'], -0.86263231)


        # Two unequal Gaussian peaks, next to each other
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+20)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-20)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double11.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.1586310125)
        self.assertAlmostEqual(stats['stddev']*1e7, 2.573732986)
        self.assertAlmostEqual(stats['skew'], 1.9572166)
        self.assertAlmostEqual(stats['kurtosis'], 2.96265432)

        # Two unequal Gaussian peaks, slightly overlapping
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+10)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-10)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double12.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.15872275)
        self.assertAlmostEqual(stats['stddev']*1e7, 2.573209197)
        self.assertAlmostEqual(stats['skew'], 1.957711629)
        self.assertAlmostEqual(stats['kurtosis'], 2.964457311)

        # Two unequal Gaussian peaks, largely overlapping
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+5)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-5)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double13.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.15872275)
        self.assertAlmostEqual(stats['stddev']*1e7, 2.65973335)
        self.assertAlmostEqual(stats['skew'], 1.84573887)
        self.assertAlmostEqual(stats['kurtosis'], 2.4994102)

        # Two unequal peaks on the edges of the light curve
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+25)**2)/25.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-25)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double14.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.150463628)
        self.assertAlmostEqual(stats['stddev']*1e7, 2.60591588)
        self.assertAlmostEqual(stats['skew'], 1.9595226)
        self.assertAlmostEqual(stats['kurtosis'], 2.926038515)

        # Three unequal Gaussian peaks, next to each other
        gauss = 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+20)**2)/25.)
        gauss += 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float))**2)/5.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-20)**2)/15.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double21.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.178447649)
        self.assertAlmostEqual(stats['stddev']*1e7, 2.5243424)
        self.assertAlmostEqual(stats['skew'], 1.87494360)
        self.assertAlmostEqual(stats['kurtosis'], 2.80140004)
        
        # Three unequal Gaussian peaks, overlapping
        gauss = 0.4*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+6)**2)/5.)
        gauss += 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-8)**2)/3.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float))**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double22.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.18947657)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.13672913)
        self.assertAlmostEqual(stats['skew'], 1.37923736)
        self.assertAlmostEqual(stats['kurtosis'], 0.40229112)
        
        # Three unequal Gaussian peaks, overlapping, but shifted compared to previous
        gauss = 0.4*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+11)**2)/5.)
        gauss += 0.3*numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)-3)**2)/3.)
        gauss += numpy.exp(-((numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)+5)**2)/25.)
        lightcurve.fluxes = fluxes * (1 + gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "double23.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 1.18947657)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.13672913)
        self.assertAlmostEqual(stats['skew'], 1.37923736)
        self.assertAlmostEqual(stats['kurtosis'], 0.40229112)

    def test_constant_derivative(self):
        """Light curves with an unchanging derivate"""

        npoints = 60  # number of datapoints
        inttime = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            obstimes=numpy.array([timezero + timedelta(0, s) for s in 
                      numpy.arange(0, npoints*inttime, inttime, dtype=numpy.float)]),
            inttimes=numpy.ones(npoints, dtype=numpy.float) * inttime,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            sourceids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6
        change = numpy.linspace(1, 10, num=fluxes.shape[0])

        # Linear increase
        lightcurve.fluxes = fluxes * change
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant11.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 5.5)
        self.assertAlmostEqual(stats['stddev']*1e6, 2.664038013)
        self.assertAlmostEqual(stats['skew'], 0.)
        self.assertAlmostEqual(stats['kurtosis'], -1.26014481)
        
        # Linear decrease
        lightcurve.fluxes = fluxes * change[::-1]
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant12.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e6, 5.5)
        self.assertAlmostEqual(stats['stddev']*1e6, 2.664038013)
        self.assertAlmostEqual(stats['skew'], 0.)
        self.assertAlmostEqual(stats['kurtosis'], -1.26014481)
        
        # Quadratic increase
        lightcurve.fluxes = fluxes * change * change
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant21.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e5, 3.722881356)
        self.assertAlmostEqual(stats['stddev']*1e5, 2.997230982)
        self.assertAlmostEqual(stats['skew'], 0.530594134)
        self.assertAlmostEqual(stats['kurtosis'], -1.0226088379)
        
        # Quadratic decrease
        lightcurve.fluxes = fluxes * change[::-1] * change[::-1]
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant22.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e5, 3.722881356)
        self.assertAlmostEqual(stats['stddev']*1e5, 2.997230982)
        self.assertAlmostEqual(stats['skew'], 0.530594134)
        self.assertAlmostEqual(stats['kurtosis'], -1.0226088379)

        # Exponential increase
        lightcurve.fluxes = fluxes * numpy.exp(change)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant31.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean'], 0.002594539)
        self.assertAlmostEqual(stats['stddev'], 0.0049424894)
        self.assertAlmostEqual(stats['skew'], 2.3239532572)
        self.assertAlmostEqual(stats['kurtosis'], 4.812191265)

        # Exponential decrease
        lightcurve.fluxes = fluxes * numpy.exp(change[::-1])
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant32.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean'], 0.002594539)
        self.assertAlmostEqual(stats['stddev'], 0.0049424894)
        self.assertAlmostEqual(stats['skew'], 2.3239532572)
        self.assertAlmostEqual(stats['kurtosis'], 4.812191265)

        maximum = max(numpy.exp(change))
        # Inverse exponential increase
        lightcurve.fluxes = fluxes * (maximum - numpy.exp(change) + 1)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant33.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean'], 0.0194329267)
        self.assertAlmostEqual(stats['stddev'], 0.0049424894)
        self.assertAlmostEqual(stats['skew'], -2.323953257)
        self.assertAlmostEqual(stats['kurtosis'], 4.812191265)

        # Inverse exponential decrease
        lightcurve.fluxes = fluxes * (maximum - numpy.exp(change[::-1]) + 1)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "constant34.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean'], 0.0194329267)
        self.assertAlmostEqual(stats['stddev'], 0.0049424894)
        self.assertAlmostEqual(stats['skew'], -2.323953257)
        self.assertAlmostEqual(stats['kurtosis'], 4.812191265)

    def test_dipping(self):
        """Light curves dropping below background"""

        npoints = 60  # number of datapoints
        inttime = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            obstimes=numpy.array([timezero + timedelta(0, s) for s in 
                      numpy.arange(0, npoints*inttime, inttime, dtype=numpy.float)]),
            inttimes=numpy.ones(npoints, dtype=numpy.float) * inttime,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            sourceids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6
        change = numpy.linspace(1, 10, num=fluxes.shape[0])
        lightcurve.fluxes = fluxes 
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2, dtype=numpy.float)**2)/3.)
        lightcurve.fluxes = fluxes * (1 - gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "dipping1.png", background=background)
        stats = lcmod.stats(lightcurve)
        self.assertAlmostEqual(stats['mean']*1e7, 9.488336646)
        self.assertAlmostEqual(stats['stddev']*1e7, 1.8474562)
        self.assertAlmostEqual(stats['skew'], -3.84713153)
        self.assertAlmostEqual(stats['kurtosis'], 14.2676929)
        # Get the stats, but this time without the background section
        stats = lcmod.stats(lightcurve, -background[2])
        self.assertAlmostEqual(stats['mean']*1e7, 4.079486205)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.213942131)
        self.assertAlmostEqual(stats['skew'], -0.0053052801)
        self.assertAlmostEqual(stats['kurtosis'], -2.035518404)


        # Increasing the number of points gives a better background estimate,
        npoints = 180  # number of datapoints
        inttime = 60  # seconds
        timezero = datetime(2010, 10, 1, 12, 0, 0)
        lightcurve = lcmod.LightCurve(
            obstimes=numpy.array([timezero + timedelta(0, s) for s in 
                      numpy.arange(0, npoints*inttime, inttime,
                                   dtype=numpy.float)]),
            inttimes=numpy.ones(npoints, dtype=numpy.float) * inttime,
            fluxes=numpy.ones(npoints, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(npoints, dtype=numpy.float) * 1e-8,
            sourceids=numpy.arange(0, npoints)
        )
        fluxes = numpy.ones(npoints, dtype=numpy.float) * 1e-6
        change = numpy.linspace(1, 10, num=fluxes.shape[0])
        lightcurve.fluxes = fluxes 
        gauss = numpy.exp(-(numpy.arange(-npoints/2, npoints/2,
                                         dtype=numpy.float)**2)/3.)
        lightcurve.fluxes = fluxes * (1 - gauss)
        background = lcmod.calc_background(lightcurve)
        plot_lightcurve(lightcurve, "dipping2.png", background=background)
        stats = lcmod.stats(lightcurve)
        # Note how the statistics change when more background data is available,
        # when compared to the previous case
        self.assertAlmostEqual(stats['mean']*1e7, 9.82944555)
        self.assertAlmostEqual(stats['stddev']*1e7, 1.087882855)
        self.assertAlmostEqual(stats['skew'], -7.17736487336)
        self.assertAlmostEqual(stats['kurtosis'], 53.3102313227)
        # Get the stats, but this time without the background section
        # Now, the statistics are the same as the previous case, even with
        # more background data
        stats = lcmod.stats(lightcurve, -background[2])
        self.assertAlmostEqual(stats['mean']*1e7, 4.079486205)
        self.assertAlmostEqual(stats['stddev']*1e7, 3.213942131)
        self.assertAlmostEqual(stats['skew'], -0.0053052801)
        self.assertAlmostEqual(stats['kurtosis'], -2.035518404)

    def test_periodic(self):
        """Various periodic light curves"""

        pass


def greg_to_julian(year, month=None, day=None, hour=0, minute=0, seconds=0.):
    if isinstance(year, datetime):
        yyear = year.year
        month = year.month
        day = year.day
        hour = year.hour
        minute = year.minute
        second = year.second
        year = yyear
    jd = 0.0
    if month > 12 or month < 1:
        raise ValueError, 'Month out of range'
    if day < 1 or day > 32:
        raise ValueError, 'Day out of range'
    iyear = year
    imonth = month
    iday = int (day)
    dayfrac = day - iday
    if iyear < 0:
        iyear = iyear + 1
    if month > 2:
        imonth = month + 1
    else:
        iyear = iyear - 1
        imonth = month + 13
    jd = math.floor(365.25 * iyear) + math.floor(30.6001 * imonth) + iday + 1720995
    if (iday + 31 * (month + 12 * year)) >= (15 + 31 * (10 + 12 * 1582)):
        corr = int (0.01 * iyear)
        jd = jd + 2 - corr + int (0.25 * corr)
    jd = jd + dayfrac - 0.5
    dayfrac = hour/24. + minute/1440. + second/86400.
    jd = jd + dayfrac
    return jd
    
        
def plot_lightcurve(lightcurve, filename, background=None):
    """Small helper function"""
    if ENABLE_PLOTTING:
        figure = Figure()
        canvas = FigureCanvas(figure)
        axes = figure.add_subplot(1, 1, 1)
        obstimes = numpy.array([greg_to_julian(obstime) for obstime in
                                lightcurve.obstimes])
        axes.errorbar(obstimes, lightcurve.fluxes,
                      lightcurve.errors, lightcurve.inttimes/2./86400.)
        if background:
            mean, sigma, indices = background
            start = None
            for i in numpy.where(indices)[0]:
                if start is None:
                    start = stop = i
                elif stop == i-1:
                    stop = i
                else:
                    axes.plot(obstimes[numpy.array(range(start, stop+1))],
                              mean*numpy.ones((stop-start+1),),
                              color='red', linewidth=3)
                    start = None
            if start is not None and stop > start:
                ind = numpy.array(range(start, stop+1))
                axes.plot(obstimes[numpy.array(range(start, stop+1))],
                          mean*numpy.ones((stop-start+1),), color='red',
                          linewidth=3)
            axes.plot([obstimes[0], obstimes[0]], [mean-sigma, mean+sigma],
                      color='orange')
            axes.plot([obstimes[0], obstimes[-1]], [mean, mean],
                      color='red', linestyle='-.')
            limits = [min(lightcurve.fluxes), max(lightcurve.fluxes)]
            delta = limits[1] - limits[0]
            axes.set_ylim(limits[0] - 0.1*delta-max(lightcurve.errors),
                          limits[1] + 0.1*delta+max(lightcurve.errors))
        canvas.print_figure(filename)

        
if __name__ == '__main__':
    unittest.main()
