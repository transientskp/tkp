"""
Tests for elliptical Gaussian fitting code in the TKP pipeline.
"""
import unittest

import numpy

from tkp.sourcefinder.extract import source_profile_and_errors
from tkp.sourcefinder.fitting import moments, fitgaussian, FIT_PARAMS
from tkp.sourcefinder.gaussian import gaussian
from tkp.sourcefinder.utils import fudge_max_pix, calculate_beamsize, maximum_pixel_method_variance, \
    calculate_correlation_lengths

# The units that are tested often require information about the resolution element:
# (semimajor(pixels),semiminor(pixels),beam position angle (radians).
# Please enter some reasonable restoring beam here.
beam = (2.5, 2., 0.5)


class SimpleGaussTest(unittest.TestCase):
    """Generic, easy-to-fit elliptical Gaussian"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.height = 10
        self.x = 250
        self.y = 250
        self.maj = 40
        self.min = 20
        self.theta = 0
        self.mygauss = numpy.ma.array(
            gaussian(self.height, self.x, self.y, self.maj, self.min,
                     self.theta)(Xin, Yin))
        self.beamsize = calculate_beamsize(self.maj, self.min)
        self.fudge_max_pix_factor = fudge_max_pix(self.maj, self.min, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        self.fit = fitgaussian(self.mygauss, self.moments)

    def testHeight(self):
        self.assertEqual(self.mygauss.max(), self.height)

    def testFitHeight(self):
        self.assertAlmostEqual(self.fit["peak"], self.height)

    def testMomentPosition(self):
        self.assertAlmostEqual(self.moments["xbar"], self.x)
        self.assertAlmostEqual(self.moments["ybar"], self.y)

    def testFitPosition(self):
        self.assertAlmostEqual(self.fit["xbar"], self.x)
        self.assertAlmostEqual(self.fit["ybar"], self.y)

    def testMomentSize(self):
        self.assertAlmostEqual(self.moments["semimajor"], self.maj, 3)
        self.assertAlmostEqual(self.moments["semiminor"], self.min, 3)

    def testFitSize(self):
        self.assertAlmostEqual(self.fit["semimajor"], self.maj)
        self.assertAlmostEqual(self.fit["semiminor"], self.min)

    def testMomentAngle(self):
        self.assertAlmostEqual(self.moments["theta"], self.theta)

    def testFitAngle(self):
        self.assertAlmostEqual(self.fit["theta"], self.theta)


class NegativeGaussTest(SimpleGaussTest):
    """Negative Gaussian"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.height = -10
        self.x = 250
        self.y = 250
        self.maj = 40
        self.min = 20
        self.theta = 0
        self.mygauss = numpy.ma.array(
            gaussian(self.height, self.x, self.y, self.maj, self.min,
                     self.theta)(Xin, Yin))
        self.beamsize = calculate_beamsize(self.maj, self.min)
        self.fudge_max_pix_factor = fudge_max_pix(self.maj, self.min, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        self.fit = fitgaussian(self.mygauss, self.moments)

    def testHeight(self):
        self.assertEqual(self.mygauss.min(), self.height)


class CircularGaussTest(SimpleGaussTest):
    """Circular Gaussian: it makes no sense to measure a rotation angle"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.height = 10
        self.x = 250
        self.y = 250
        self.maj = 40
        self.min = 40
        self.theta = 0
        self.mygauss = numpy.ma.array(
            gaussian(self.height, self.x, self.y, self.maj, self.min,
                     self.theta)(Xin, Yin))
        self.beamsize = calculate_beamsize(self.maj, self.min)
        self.fudge_max_pix_factor = fudge_max_pix(self.maj, self.min, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        self.fit = fitgaussian(self.mygauss, self.moments)

    def testMomentAngle(self):
        pass

    def testFitAngle(self):
        pass


class NarrowGaussTest(SimpleGaussTest):
    """Only 1 pixel wide"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.height = 10
        self.x = 250
        self.y = 250
        self.maj = 40
        self.min = 1
        self.theta = 0
        self.mygauss = numpy.ma.array(gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin,
                                                                         Yin))
        self.beamsize = calculate_beamsize(self.maj, self.min)
        self.fudge_max_pix_factor = fudge_max_pix(self.maj, self.min, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        self.fit = fitgaussian(self.mygauss, self.moments)


class RotatedGaussTest(SimpleGaussTest):
    """Rotated by an angle < pi/2"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.height = 10
        self.x = 250
        self.y = 250
        self.maj = 40
        self.min = 20
        self.theta = numpy.pi / 4
        self.mygauss = numpy.ma.array(gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin,
                                                                         Yin))
        self.beamsize = calculate_beamsize(self.maj, self.min)
        self.fudge_max_pix_factor = fudge_max_pix(self.maj, self.min, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        self.fit = fitgaussian(self.mygauss, self.moments)

    def testMomentAngle(self):
        self.assertAlmostEqual(self.moments["theta"], self.theta)


class RotatedGaussTest2(SimpleGaussTest):
    """Rotated by an angle > pi/2; theta becomes negative"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.height = 10
        self.x = 250
        self.y = 250
        self.maj = 40
        self.min = 20
        self.theta = 3 * numpy.pi / 4
        self.mygauss = numpy.ma.array(gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin,
                                                                         Yin))
        self.beamsize = calculate_beamsize(self.maj, self.min)
        self.fudge_max_pix_factor = fudge_max_pix(self.maj, self.min, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        self.fit = fitgaussian(self.mygauss, self.moments)

    def testMomentAngle(self):
        self.assertAlmostEqual(self.moments["theta"], self.theta - numpy.pi)

    def testFitAngle(self):
        self.assertAlmostEqual(self.fit["theta"], self.theta - numpy.pi)


class AxesSwapGaussTest(SimpleGaussTest):
    """We declare the axes the wrong way round: the fit should reverse them &
    change the angle"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.height = 10
        self.x = 250
        self.y = 250
        self.maj = 20
        self.min = 40
        self.theta = 0
        self.mygauss = numpy.ma.array(gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin,
                                                                         Yin))
        self.beamsize = calculate_beamsize(self.maj, self.min)
        self.fudge_max_pix_factor = fudge_max_pix(self.maj, self.min, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        self.fit = fitgaussian(self.mygauss, self.moments)

    def testMomentAngle(self):
        theta = self.moments["theta"]
        # Numpy 1.6 and 1.9 return -pi/2 and +pi/2, respectively.
        # Presumably there's some numerical quirk causing different,
        # but equivalent, convergence in the optimization.
        if theta < 0:
            theta = theta + numpy.pi
        self.assertAlmostEqual(theta, numpy.pi / 2)

    def testFitAngle(self):
        theta = self.fit["theta"]
        # Numpy 1.6 and 1.9 return -pi/2 and +pi/2, respectively.
        # Presumably there's some numerical quirk causing different,
        # but equivalent, convergence in the optimization.
        if theta < 0:
            theta = theta + numpy.pi
        self.assertAlmostEqual(theta, numpy.pi / 2)

    def testMomentSize(self):
        self.assertAlmostEqual(self.moments["semiminor"], self.maj, 5)
        self.assertAlmostEqual(self.moments["semimajor"], self.min, 5)

    def testFitSize(self):
        self.assertAlmostEqual(self.fit["semiminor"], self.maj)
        self.assertAlmostEqual(self.fit["semimajor"], self.min)


class RandomGaussTest(unittest.TestCase):
    """Should not be possible to fit a Gaussian to random data. You can still
    measure moments, though -- things should be fairly evenly distributed."""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.mygauss = numpy.random.random(Xin.shape)
        self.beamsize = calculate_beamsize(beam[0], beam[1])
        self.fudge_max_pix_factor = fudge_max_pix(beam[0], beam[1], beam[2])

    def testMoments(self):
        try:
            moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)
        except:
            self.fail('Moments method failed to run.')


class NoisyGaussTest(unittest.TestCase):
    """Test calculation of chi-sq and fitting in presence of (artificial) noise"""

    def setUp(self):
        Xin, Yin = numpy.indices((500, 500))
        self.peak = 10
        self.xbar = 250
        self.ybar = 250
        self.semimajor = 40
        self.semiminor = 20
        self.theta = 0
        self.mygauss = numpy.ma.array(
            gaussian(self.peak, self.xbar, self.ybar,
                     self.semimajor, self.semiminor, self.theta)(Xin, Yin))
        self.beamsize = calculate_beamsize(self.semimajor, self.semiminor)
        self.fudge_max_pix_factor = fudge_max_pix(self.semimajor, self.semiminor, self.theta)
        self.moments = moments(self.mygauss, self.fudge_max_pix_factor, self.beamsize, 0)

    def test_tiny_pixel_offset(self):
        pixel_noise = 0.0001
        self.mygauss[self.xbar + 30, self.ybar] += pixel_noise
        self.fit = fitgaussian(self.mygauss, self.moments)
        for param in FIT_PARAMS:
            self.assertAlmostEqual(getattr(self, param), self.fit[param],
                                   places=6)

    def test_small_pixel_offset(self):
        pixel_noise = 0.001
        n_noisy_pix = 2
        # Place noisy pix symmetrically about centre to avoid position offset
        self.mygauss[self.xbar + 30, self.ybar] += pixel_noise
        self.mygauss[self.xbar - 30, self.ybar] += pixel_noise
        self.fit = fitgaussian(self.mygauss, self.moments)

        for param in FIT_PARAMS:
            self.assertAlmostEqual(getattr(self, param), self.fit[param],
                                   places=5)

    def test_noisy_background(self):
        # Use a fixed random state seed, so unit-test is reproducible:
        rstate = numpy.random.RandomState(42)
        pixel_noise = 0.5
        self.mygauss += rstate.normal(scale=pixel_noise,
                                      size=len(self.mygauss.ravel())).reshape(
            self.mygauss.shape)
        self.fit = fitgaussian(self.mygauss, self.moments)
        self.longMessage = True  # Show assertion fail values + given message

        # First, let's check we've converged to a reasonable fit in the
        # presence of noise:
        # print
        for param in FIT_PARAMS:
            # print param, getattr(self,param), self.fit[param]
            self.assertAlmostEqual(getattr(self, param), self.fit[param],
                                   places=1,
                                   msg=param + " misfit (bad random noise seed?)",
                                   )

        # Now we run the full error-profiling routine and check the chi-sq
        # calculations:
        self.fit_w_errs, _ = source_profile_and_errors(
            data=self.mygauss,
            threshold=0.,
            noise=pixel_noise,
            beam=(self.semimajor, self.semiminor, self.theta),
            fudge_max_pix_factor=fudge_max_pix(self.semimajor, self.semiminor, self.theta),
            max_pix_variance_factor=maximum_pixel_method_variance(self.semimajor, self.semiminor, self.theta),
            correlation_lengths=calculate_correlation_lengths(self.semimajor, self.semiminor),
            beamsize=calculate_beamsize(self.semimajor, self.semiminor)
        )

        npix = len(self.mygauss.ravel())
        # print "CHISQ", npix, self.fit_w_errs.chisq

        # NB: this is the calculation for reduced chisq in presence of
        # independent pixels, i.e. uncorrelated noise.
        # For real data, we try to take the noise-correlation into account.
        # print "Reduced chisq", self.fit_w_errs.chisq / npix
        self.assertTrue(0.9 < self.fit_w_errs.chisq / npix < 1.1)
