import unittest
import numpy
from numpy.testing import assert_array_equal
from tkp.sourcefinder.utils import circular_mask

class test_circular_mask(unittest.TestCase):
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

    def test_known_results(self):
        for parameters, result in self.known_results:
            assert_array_equal(circular_mask(*parameters), result)

if __name__ == "__main__":
    unittest.main()
