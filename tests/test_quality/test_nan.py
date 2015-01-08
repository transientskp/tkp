import unittest
import numpy as np
from tkp.quality.nan import contains_nan


class TestNan(unittest.TestCase):
    def test_valid(self):
        array = np.array([1, 2, 3.0])
        self.assertFalse(contains_nan(array))

    def test_invalid(self):
        array = np.array([1, 2, np.nan])
        result = contains_nan(array)
        self.assertTrue(result)

    def test_errorstring(self):
        array = np.array([1, 2, np.nan])
        result = contains_nan(array)
        self.assertTrue(type(result) == str)
