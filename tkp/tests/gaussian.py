# Tests for elliptical Gaussian fitting code in the TKP pipeline.

import unittest
import tkp.sourcefinder.gaussian as gaussian
import numpy

# The units that are tested often require information about the resolution element:
# (semimajor(pixels),semiminor(pixels),beam position angle (radians).
# Please enter some reasonable restoring beam here.
beam=(2.5,2.,0.5)

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
        self.mygauss = numpy.ma.array(gaussian.gaussian(self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin, Yin))
        self.moments = gaussian.moments(self.mygauss, beam, 0)
        self.fit = gaussian.fitgaussian(self.mygauss, self.moments)

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
        self.mygauss = numpy.ma.array(gaussian.gaussian(self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin, Yin))
        self.moments = gaussian.moments(self.mygauss, beam, 0)
        self.fit = gaussian.fitgaussian(self.mygauss, self.moments)

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
        self.mygauss = numpy.ma.array(gaussian.gaussian(self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin, Yin))
        self.moments = gaussian.moments(self.mygauss, beam, 0)
        self.fit = gaussian.fitgaussian(self.mygauss, self.moments)

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
        self.mygauss = numpy.ma.array(gaussian.gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin, Yin))
        self.moments = gaussian.moments(self.mygauss, beam, 0)
        self.fit = gaussian.fitgaussian(self.mygauss, self.moments)

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
        self.mygauss = numpy.ma.array(gaussian.gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin, Yin))
        self.moments = gaussian.moments(self.mygauss, beam, 0)
        self.fit = gaussian.fitgaussian(self.mygauss, self.moments)

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
        self.mygauss = numpy.ma.array(gaussian.gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin, Yin))
        self.moments = gaussian.moments(self.mygauss, beam, 0)
        self.fit = gaussian.fitgaussian(self.mygauss, self.moments)

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
        self.mygauss = numpy.ma.array(gaussian.gaussian(
            self.height, self.x, self.y, self.maj, self.min, self.theta)(Xin, Yin))
        self.moments = gaussian.moments(self.mygauss, beam, 0)
        self.fit = gaussian.fitgaussian(self.mygauss, self.moments)

    def testMomentAngle(self):
        self.assertAlmostEqual(self.moments["theta"], -1 * numpy.pi/2)

    def testFitAngle(self):
        self.assertAlmostEqual(self.fit["theta"], -1 * numpy.pi/2)

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

    def testMoments(self):
        try:
            gaussian.moments(self.mygauss, beam, 0)
        except:
            fail('Moments method failed to run.')

if __name__ == '__main__':
    unittest.main()
