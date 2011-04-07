#! /usr/bin/env python

"""

Unit test for feature extraction, used in the classification pipeline

Some unittests also serve as examples.For example, the background
calculation tests (test_calc_background) show what happens when not
enough background data is/are available.

"""


import sys, os
import unittest
from optparse import OptionParser
from datetime import datetime, timedelta
import logging
import numpy
from tkp.database.database import connection as dbconnection
from tkp.classification.features import lightcurve
from tkp.classification.manual import DateTime


# Setting DEBUG to True will produce output through the loggers in the
# various tkp.classification.features routines
DEBUG = False



class TestLightcurve(unittest.TestCase):
    """  """

    def setUp(self):
        self.logger = logging.getLogger()
        if DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.CRITICAL)

        # create test data
        self.timezero = datetime(2010, 10, 1, 12, 0, 0)
        self.lightcurve = dict(
            obstimes=numpy.array([self.timezero + timedelta(0, s) for s in 
                      numpy.arange(0, 30*60, 60, dtype=numpy.float)]),
            inttimes=numpy.ones(30, dtype=numpy.float) * 60,
            fluxes=numpy.ones(30, dtype=numpy.float) * 1e-6,
            errors=numpy.ones(30, dtype=numpy.float) * 1e-8,
            sourceid=numpy.arange(0, 30)
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
        self.lightcurve['fluxes'] += numpy.array(errors)


    def tearDown(self):
        pass
        
    def test_calc_background(self):
        lc = self.lightcurve
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices.all(), True)

        # Corner cases first
        # transient at start
        lc['fluxes'][0] *= 4.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices[1:].all(), True)
        self.assertEqual(indices[0], False)

        # transient on first two light curve points
        lc['fluxes'][1] *= 2.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices[2:].all(), True)
        self.assertEqual(indices[0:2].any(), False)

        # transient near very end
        lc['fluxes'][0] /= 4.
        lc['fluxes'][1] /= 2.
        lc['fluxes'][-1] *= 4.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices[:-1].all(), True)
        self.assertEqual(indices[-1], False)

        # transient at last two light curve points
        lc['fluxes'][-2] *= 2.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices[:-2].all(), True)
        self.assertEqual(indices[-2:].any(), False)

        # single peak transient
        lc['fluxes'][-1] /= 4.
        lc['fluxes'][-2] /= 2.
        lc['fluxes'][6] *= 4.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices[:6].all(), True)
        self.assertEqual(indices[7:].all(), True)
        self.assertEqual(indices[6], False)

        # longer transient
        lc['fluxes'][5] *= 2.
        lc['fluxes'][7] *= 2.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices[:5].all(), True)
        self.assertEqual(indices[8:].all(), True)
        self.assertEqual(indices[5:8].any(), False)

        # Double peaked transient        
        lc['fluxes'][15] *= 4.
        lc['fluxes'][16] *= 8.
        lc['fluxes'][17] *= 4.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-6)
        self.assertAlmostEqual(sigma, 1.01e-8)
        self.assertEqual(indices[:5].all(), True)
        self.assertEqual(indices[8:15].all(), True)
        self.assertEqual(indices[18:].all(), True)
        self.assertEqual(indices[5:8].any(), False)
        self.assertEqual(indices[15:18].any(), False)

        # Demonstrate that with not enough background points,
        # we get incorrect results
        lc['fluxes'][17] *= 2.
        lc['fluxes'][18] *= 4.
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        # Different mean & sigma!
        self.assertAlmostEqual(mean, 1.39325e-06)
        self.assertAlmostEqual(sigma, 9.5867249e-07)
        self.assertEqual(indices[:16].all(), True)
        self.assertEqual(indices[18:].all(), True)
        self.assertEqual(indices[16:17].any(), False)

        # Add extra data to the background;
        # now results are correct
        errors = [5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9, 8e-9, -8e-9,
                  2e-8, -2e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
                  2.5e-8, -2.5e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
                  1.5e-8, -1.5e-8, 5e-9, -5e-9, 1e-8, -1e-8]
        fluxes = numpy.ones(30) * 1.0e-6 + numpy.array(errors)
        lc['fluxes'] = numpy.append(lc['fluxes'], fluxes)
        lc['errors'] = numpy.append(lc['errors'], numpy.ones(30) * 1.0e-8)
        lc['obstimes'] = numpy.append(lc['obstimes'],
                                      numpy.array(
            [self.timezero + timedelta(0, s) for s in 
             numpy.arange(30*60, 60*60, 60, dtype=numpy.float)]))
        lc['inttimes'] = numpy.append(lc['inttimes'], numpy.ones(30) * 60)
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.00e-06)
        self.assertAlmostEqual(sigma, 1.01e-08)
        self.assertEqual(indices[:5].all(), True)
        self.assertEqual(indices[8:15].all(), True)
        self.assertEqual(indices[19:].all(), True)
        self.assertEqual(indices[5:8].any(), False)
        self.assertEqual(indices[15:19].any(), False)

        # steadily increasing background
        lc['fluxes'] = numpy.linspace(1.0e-6, 1.0e-4, 60)
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 5.05e-05)
        self.assertAlmostEqual(sigma, 2.93044e-05)
        self.assertEqual(indices.all(), True)

        # similar, but now increasing exponentially
        lc['fluxes'] = numpy.logspace(-6, -4, 60)
        mean, sigma, indices = lightcurve.calc_background(
            lc)
        self.assertAlmostEqual(mean, 1.4318e-05)
        self.assertAlmostEqual(sigma, 1.5397e-05)
        self.assertEqual(indices[:53].all(), True)
        self.assertEqual(indices[53:].any(), False)
        

    def test_calc_duration(self):
        obstimes = self.lightcurve['obstimes']
        inttimes = self.lightcurve['inttimes']
        indices = numpy.ones(30, dtype=numpy.bool)

        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, None)
        self.assertEqual(tend, None)
        self.assertEqual(duration, None)

        # Corner cases first
        # transient at start
        indices[0] = False
        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 0, 30, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 1, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 30.0)

        # transient on first two light curve points
        indices[1] = False
        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 0, 30, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 2, 0, 0, 30.0))        
        self.assertAlmostEqual(duration, 90.0)

        # transient near very end
        indices[0] = indices[1] = True
        indices[-1] = False
        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 29, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 29, 30, 0, 30.0))
        self.assertAlmostEqual(duration, 30.0)

        # transient at last two light curve points
        indices[-2] = False
        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 28, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 29, 30, 0, 30.0))
        self.assertAlmostEqual(duration, 90.0)

        # single peak transient
        # transient at last two light curve points
        indices[-1] = indices[-2] = True
        indices[6] = False
        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 6, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 7, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 60.0)

        # longer transient
        indices[5] = indices[7] = False
        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 5, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 8, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 180.0)

        # Double peaked transient
        indices[15] = indices[16] = indices[17] = indices[18] = False
        tzero, tend, duration = lightcurve.calc_duration(
            obstimes, inttimes, indices)
        self.assertEqual(tzero, DateTime(2010, 10, 1, 12, 5, 0, 0, 30.0))
        self.assertEqual(tend, DateTime(2010, 10, 1, 12, 19, 0, 0, 30.0))
        self.assertAlmostEqual(duration, 840.0)

    def test_calc_fluxincrease(self):
        lc = self.lightcurve
        background = {'mean': 1.0e-6, 'sigma': 1.0e-8}
        indices = numpy.ones(30, dtype=numpy.bool)

        # (0.0, {}, None)
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 0.0)
        self.assertEqual(increase, {})
        self.assertEqual(ipeak, None)

        # (2.0099999999999998e-06, {'percent': 2.0099999999999998, 'absolute': 1.0099999999999999e-06}, 0)
        indices[0] = False
        lc['fluxes'][0] *= 2.
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 2.0e-6)
        self.assertAlmostEqual(increase['percent'], 2.01)
        self.assertAlmostEqual(increase['absolute'], 1.0e-6)
        self.assertEqual(ipeak, 0)

        # (4.0199999999999996e-06, {'percent': 4.0199999999999996, 'absolute': 3.0199999999999999e-06}, 0)
        indices[1] = False
        lc['fluxes'][0] *= 2.
        lc['fluxes'][1] *= 2.
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 4.0e-6)
        self.assertAlmostEqual(increase['percent'], 4.02)
        self.assertAlmostEqual(increase['absolute'], 3.0e-6)
        self.assertEqual(ipeak, 0)

        indices[0] = indices[1] = True
        indices[-1] = False
        lc['fluxes'][0] /= 4.
        lc['fluxes'][1] /= 2.
        lc['fluxes'][-1] *= 2.
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 1.98e-6)
        self.assertAlmostEqual(increase['percent'], 1.98)
        self.assertAlmostEqual(increase['absolute'], 9.8e-7)
        self.assertEqual(ipeak, 29)

        indices[-2] = False
        lc['fluxes'][-1] *= 2.
        lc['fluxes'][-2] *= 2.
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 3.96e-6)
        self.assertAlmostEqual(increase['percent'], 3.96)
        self.assertAlmostEqual(increase['absolute'], 2.96e-6)
        self.assertEqual(ipeak, 29)

        indices[-2] = indices[-1] = True
        indices[6] = False
        lc['fluxes'][-1] /= 4.
        lc['fluxes'][-2] /= 2.
        lc['fluxes'][6] *= 2.
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 2.02e-6)
        self.assertAlmostEqual(increase['percent'], 2.016)
        self.assertAlmostEqual(increase['absolute'], 1.02e-6)
        self.assertEqual(ipeak, 6)

        indices[5] = indices[7] = False
        lc['fluxes'][5] *= 2.
        lc['fluxes'][6] *= 2.
        lc['fluxes'][7] *= 2.
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 4.03e-6)
        self.assertAlmostEqual(increase['percent'], 4.032)
        self.assertAlmostEqual(increase['absolute'], 3.03e-6)
        self.assertEqual(ipeak, 6)

        indices[15] = indices[16] = indices[17] = indices[18] = False
        lc['fluxes'][15] *= 4.
        lc['fluxes'][16] *= 8.
        lc['fluxes'][17] *= 8.
        lc['fluxes'][18] *= 4.
        peakflux, increase, ipeak = lightcurve.calc_fluxincrease(
            lc, background, indices)
        self.assertAlmostEqual(peakflux, 8.2e-6)
        self.assertAlmostEqual(increase['percent'], 8.2)
        self.assertAlmostEqual(increase['absolute'], 7.2e-6)
        self.assertEqual(ipeak, 16)

    def test_calc_risefall(self):
        lc = self.lightcurve
        background = {'mean': 1.0e-6, 'sigma': 1.0e-8}
        indices = numpy.ones(30, dtype=numpy.bool)

        ipeak = None
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        # all zeroes are integers!
        self.assertEqual(rise['time'], 0)
        self.assertEqual(rise['flux'], 0)
        self.assertEqual(fall['time'], 0)
        self.assertEqual(fall['flux'], 0)
        self.assertEqual(ratio, 0)

        ipeak = 0
        indices[0] = False
        lc['fluxes'][0] *= 2.
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertEqual(rise['time'], 0)  # integer!
        self.assertAlmostEqual(rise['flux'], 1.0e-6)
        self.assertAlmostEqual(fall['time'], 60.0)
        self.assertAlmostEqual(fall['flux'], 1.0e-6)
        self.assertEqual(ratio, 0)  # integer!

        indices[1] = False
        lc['fluxes'][0] *= 2.
        lc['fluxes'][1] *= 2.
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertEqual(rise['time'], 0)  # integer!
        self.assertAlmostEqual(rise['flux'], 3.02e-6)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux'], 3.02e-6)
        self.assertEqual(ratio, 0)  # integer!

        ipeak = 29
        indices[0] = indices[1] = True
        indices[-1] = False
        lc['fluxes'][0] /= 4.
        lc['fluxes'][1] /= 2.
        lc['fluxes'][-1] *= 2.
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 60.0)
        self.assertAlmostEqual(rise['flux'], 9.8e-7)
        self.assertEqual(fall['time'], 0)  # integer!
        self.assertAlmostEqual(fall['flux'], 9.8e-7)
        self.assertEqual(ratio, 0)

        indices[-2] = False
        lc['fluxes'][-1] *= 2.
        lc['fluxes'][-2] *= 2.
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 120.0)
        self.assertAlmostEqual(rise['flux'], 2.96e-6)
        self.assertEqual(fall['time'], 0)  # integer!
        self.assertAlmostEqual(fall['flux'], 2.96e-6)
        self.assertEqual(ratio, 0)

        ipeak = 6
        indices[-2] = indices[-1] = True
        indices[6] = False
        lc['fluxes'][-1] /= 4.
        lc['fluxes'][-2] /= 2.
        lc['fluxes'][6] *= 2.
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 60.0)
        self.assertAlmostEqual(rise['flux'], 1.016e-6)
        self.assertAlmostEqual(fall['time'], 60.0)
        self.assertAlmostEqual(fall['flux'], 1.06e-6)
        self.assertAlmostEqual(ratio, 1.0)


        indices[5] = indices[7] = False
        lc['fluxes'][5] *= 2.
        lc['fluxes'][6] *= 2.
        lc['fluxes'][7] *= 2.
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 120.0)
        self.assertAlmostEqual(rise['flux'], 3.032e-6)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux'], 3.032e-6)
        self.assertAlmostEqual(ratio, 1.0)

        ipeak = 16
        indices[15] = indices[16] = indices[17] = False
        lc['fluxes'][15] *= 4.
        lc['fluxes'][16] *= 8.
        lc['fluxes'][17] *= 8.
        lc['fluxes'][18] *= 4.
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 120.0)
        self.assertAlmostEqual(rise['flux'], 7.2e-6)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux'], 7.2e-6)
        self.assertAlmostEqual(ratio, 1.0)

        # Change the duration of the second event by shifting the peak
        # so that the rise and fall ratio != 1
        # Note: normally, we'd need extra data for the background to
        # obtain correct results, as demonstrated above; in this case
        # we have manually set indices to be correct.
        lc['fluxes'][17] *= 2.
        lc['fluxes'][18] *= 2.
        indices[18] = False
        ipeak = 17
        rise, fall, ratio = lightcurve.calc_risefall(
            lc, background, indices, ipeak)
        self.assertAlmostEqual(rise['time'], 180.0)
        self.assertAlmostEqual(rise['flux'], 1.46e-5)
        self.assertAlmostEqual(fall['time'], 120.0)
        self.assertAlmostEqual(fall['flux'], 1.46e-5)
        self.assertAlmostEqual(ratio, 2/3.)
        
    
if __name__ == '__main__':
    unittest.main()
