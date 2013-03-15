import math

import unittest2 as unittest

import tkp.db
from tkp.testutil.decorators import requires_database
from tkp.testutil.db_queries import convert_to_cartesian as db_cartesian
from tkp.utility.coordinates import eq_to_cart as py_cartesian

"""Test miscellaneous minor database functions"""


@requires_database()
class TestCartesianConversions(unittest.TestCase):
    """This is a very simple function,
    but it's worth a quick check for numerical consistency,
    since we are utilising two different functions to give the same thing.
    (And if nothing else it enforces a check on future code alterations ).
    
    For known results, we use pairs of tuples; structure is: 
        ( (ra, decl), (x,y,z) )
    """
    def setUp(self):
        self.db = tkp.db.Database()

    def test_known_results(self):
        pole_results = ((0.0, 90.0),
                       (0, 0, 1.0))
        meridian_eq = ((0.0, 0.0),
                       (1.0, 0, 0))
        meridian_eq_wrap = ((360.0, 0.0),
                            (1.0, 0, 0))
        antimeridian_eq = ((180.0, 0.0),
                            (-1.0, 0, 0))
        ninety_eq = ((90, 0.0),
                     (0.0, 1.0, 0))
        fortyfive_eq = ((45, 0.0),
                     (1.0 / math.sqrt(2), 1.0 / math.sqrt(2), 0))
        fortyfive_fortyfive = ((45, 45.0),
                     (math.sin(math.radians(45)) / math.sqrt(2), 
                      math.sin(math.radians(45)) / math.sqrt(2), 
                      math.cos(math.radians(45))))

        def check_known_result(kr):
            py_result = py_cartesian(*kr[0])
            db_result = db_cartesian(self.db.connection, *kr[0])
            for i in range(3):
                self.assertAlmostEqual(kr[1][i], py_result[i])
                self.assertAlmostEqual(kr[1][i], db_result[i])

        for kr in (pole_results,
                   meridian_eq,
                   meridian_eq_wrap,
                   antimeridian_eq,
                   ninety_eq,
                   fortyfive_eq):
            check_known_result(kr)


