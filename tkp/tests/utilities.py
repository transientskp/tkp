# Tests for generic utility functions written for the TKP pipeline.

import unittest
import numpy
from tkp.utility import utilities
from tkp.utility.uncertain import Uncertain

class ErrorWeightedMeanTestCase(unittest.TestCase):
    """
    Testing our simple calculation of error-weighted means of an iterator.
    """
    def setUp(self):
        self.values = [Uncertain(x, y) for x, y in
            zip(numpy.random.random(1000), numpy.random.random(1000))
        ]

    def testMeanValue(self):
        self.assertEqual(
            utilities.error_weighted_mean(self.values).value,
            numpy.average(
                [x.value for x in self.values],
                weights=[1.0/x.error for x in self.values]
            )
        )


if __name__ == '__main__':
    unittest.main()
