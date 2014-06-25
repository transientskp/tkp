import os
import unittest
from tkp.quality.restoringbeam import beam_invalid

class TestRestoringBeam(unittest.TestCase):
    # semimaj, semimin give semi-axis lengths in pixels.
    def test_undersampled(self):
        semimaj, semimin, theta = 0.1, 0.1, 0.0
        self.assertTrue(beam_invalid(semimaj, semimin, theta))

    def test_oversampled(self):
        semimaj, semimin, theta = 100, 100, 0.0
        self.assertTrue(beam_invalid(semimaj, semimin, theta))

    def test_elliptical(self):
        semimaj, semimin, theta = 100, 0.1, 0.0
        self.assertTrue(beam_invalid(semimaj, semimin, theta))

    def test_infinite(self):
        smaj, smin, theta = float('inf'), float('inf'), float('inf')
        self.assertTrue(beam_invalid(smaj, smin, theta))

    def test_ok(self):
        semimaj, semimin, theta = 10, 5, 0.0
        self.assertFalse(beam_invalid(semimaj, semimin, theta))

if __name__ == '__main__':
    unittest.main()
