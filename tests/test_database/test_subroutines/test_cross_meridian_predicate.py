import unittest2 as unittest
from tkp.testutil.calculations import cross_meridian_predicate as py_predicate



class TestCrossMeridianPredicate(unittest.TestCase):
    """
    Checks whether sources lie across the meridian, and should hence be
    shifted by 180 degrees (and then taken modulo 360) before being 
    averaged / differenced.
    
    NB does *not* assert if they are numerically on the same wrapping, i.e. 
    CrossMeridianPredicate(10,370) -> False. 
    That must be dealt with elsewhere (sanitise inputs by always taking
    modulo 360 first?).
    
    While this sounds trivial it can be easy to miss edge or unusual cases,
    and should definitely be double checked when we're doing it in SQL.
    """
    def setUp(self):
        self.test_cases = {
                         (-1, 1): True,
                         (1, 1):False,
                         (-1, -1):False,
                         (0, -1):True,
                         (0, 1):False,
                         (1, 361):False,
                         (1, 359):True,
                         (180, 540):False,
                         (179, 541):False,
                         (179, -179):False,
                         }

    def TestPythonImplementation(self):
        for case, ans in self.test_cases.iteritems():
            self.assertEqual(py_predicate(case[0], case[1]), ans)
            self.assertEqual(py_predicate(case[1], case[0]), ans)
