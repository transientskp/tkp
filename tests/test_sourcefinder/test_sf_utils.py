import numpy
from numpy.testing import assert_array_equal
from collections import namedtuple
from tkp.utility.uncertain import Uncertain

import unittest2 as unittest

from tkp.sourcefinder.utils import maximum_pixel_method_variance, fudge_max_pix
from tkp.sourcefinder.utils import generate_result_maps
from tkp.sourcefinder.utils import circular_mask


class TestCircularMask(unittest.TestCase):
    def test_known_results(self):
        known_results = [
            ((0,0,0), numpy.zeros([0,0])),
            ((0,0,100), numpy.zeros([0,0])),
            ((1,1,0), numpy.array([[True]])),
            ((1,1,1), numpy.array([[False]])),
            ((5,1,0), numpy.array([[True],[True],[True],[True],[True]])),
            ((5,1,2), numpy.array([[True],[False],[False],[False],[True]])),
            ((1,4,0), numpy.array([[True,True,True,True]])),
            ((1,4,1), numpy.array([[True,False,False,True]]))
        ]
        for parameters, result in known_results:
            assert_array_equal(circular_mask(*parameters), result)


class TestResultMaps(unittest.TestCase):
    def testPositions(self):
        # The pixel position x, y of the source should be the same as the
        # position of the maximum in the generated result map.
        x_pos = 40
        y_pos = 60

        empty_data = numpy.zeros((100, 100))
        SrcMeasurement = namedtuple("SrcMeasurement",
            ['peak', 'x', 'y', 'smaj', 'smin', 'theta']
        )
        src_measurement = SrcMeasurement(
            peak=Uncertain(10), x=Uncertain(x_pos), y=Uncertain(y_pos),
            smaj=Uncertain(10), smin=Uncertain(10), theta=Uncertain(0)
        )
        gaussian_map, residual_map = generate_result_maps(empty_data, [src_measurement])
        gaussian_max_x = numpy.where(gaussian_map==gaussian_map.max())[0][0]
        gaussian_max_y = numpy.where(gaussian_map==gaussian_map.max())[1][0]

        self.assertEqual(gaussian_max_x, x_pos)
        self.assertEqual(gaussian_max_y, y_pos)


class UtilsTest(unittest.TestCase):
    # format: semimajor, semiminor, theta, correction, variance
    def setUp(self):
        self.correct_data = (
            ( 1.46255645752, 1.30175183614, 1.51619779602, 1.06380431709, 0.0017438970306615786 ),
            ( 1.56219151815, 1.25084762573, 1.49080535398, 1.06328376441, 0.0017765054643135159 ),
            ( 1.55231285095, 1.24513448079, 1.44660127410, 1.06398549354, 0.0018208980607872238 )
        )
    def testMaximumPixelMethodVariance(self):
        for (semimajor, semiminor, theta, correction, variance) in self.correct_data:
            self.assertEqual(maximum_pixel_method_variance(semimajor, semiminor, theta), variance)

    def testFudgeMaxPix(self):
        for (semimajor, semiminor, theta, correction, variance) in self.correct_data:
            self.assertAlmostEqual(fudge_max_pix(semimajor, semiminor, theta), correction)

