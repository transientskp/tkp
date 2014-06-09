import unittest
from tkp.utility.uncertain import Uncertain

class UncertainTestCase(unittest.TestCase):
    def test_castable_to_floating_point(self):
        """
        float(Uncertain(int(x))) should not raise.
        """
        x = Uncertain(int(0), int(0))
        self.assertFalse(isinstance(x.value, float))
        self.assertFalse(isinstance(x.error, float))
        float(x)
