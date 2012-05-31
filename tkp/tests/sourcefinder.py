__author__ = 'Gijs Molenaar'
__email__ = "gijs.molenaar@uva.nl"

import unittest

from tkp.sourcefinder.utils import maximum_pixel_method_variance, fudge_max_pix

# format: semimajor, semiminor, theta, correction, variance
correct_data = (
    ( 1.46255645752, 1.30175183614, 1.51619779602, 1.06380431709, 0.0017438970306615786 ),
    ( 1.56219151815, 1.25084762573, 1.49080535398, 1.06328376441, 0.0017765054643135159 ),
    ( 1.55231285095, 1.24513448079, 1.44660127410, 1.06398549354, 0.0018208980607867797 )
)

class UtilsTest(unittest.TestCase):
    def testMaximumPixelMethodVariance(self):
        for (semimajor, semiminor, theta, correction, variance) in correct_data:
            self.assertEqual(maximum_pixel_method_variance(semimajor, semiminor, theta), variance)

    def testFudgeMaxPix(self):
        for (semimajor, semiminor, theta, correction, variance) in correct_data:
            self.assertAlmostEqual(fudge_max_pix(semimajor, semiminor, theta), correction)

if __name__ == '__main__':
    unittest.main()

