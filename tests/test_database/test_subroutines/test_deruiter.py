import math

import unittest2 as unittest
from copy import copy

import tkp.db
from tkp.testutil.decorators import requires_database
from tkp.testutil.db_queries import convert_to_cartesian as db_cartesian
from tkp.testutil import db_subs
from tkp.db.associations import associate_extracted_sources
from tkp.testutil.db_queries import (Position,
                                     extractedsource_to_position,
                                     position_to_extractedsource)
from tkp.testutil.db_queries import deruiter as db_deruiter
from tkp.testutil.calculations import deruiter as py_deruiter
from tkp.testutil.calculations import (cross_meridian_predicate 
                                       as py_cross_meridian_predicate)
from tkp.db.orm import DataSet
from tkp.db.generic import columns_from_table

def py_dr(pair):
    return py_deruiter(pair[0], pair[1])


@requires_database()
class TestDeruiter(unittest.TestCase):
    """
    The general strategy here is as follows:
    
      - Come up with a bunch of test cases
      - Check that the python version passes in all cases
      - Check that the SQL version produces same result as python version in 
        all cases.
    """
    def setUp(self):
        self.db = tkp.db.Database()
        self.conn = self.db.connection

        # Separated in both RA and dec, away from the equator.
        self.pair1 = [Position(ra=5, dec=45,
                               ra_err=5/3600., dec_err=5/3600.),
                     Position(ra=5+3/3600., dec=45+3/3600., 
                              ra_err=5 / 3600., dec_err=5 / 3600.), ]
        # Same as pair1 but rotated 270 degrees
        self.pair2 = [self.pair1[0]._replace(ra=self.pair1[0].ra + 270),
                     self.pair1[1]._replace(ra=self.pair1[1].ra + 270), ]
        
        # Same as pair 1, but one position rotated full circle 
        # so ra1=5, ra2=365 (+ 3arcseconds)
        self.pair3 = copy(self.pair1)
        self.pair3[1] = self.pair3[1]._replace(ra=self.pair3[1].ra + 360.)

        # A nice simple case on the equator
        self.pair4 = [Position(ra=10., dec=0.,
                                ra_err=20 / 3600., dec_err=1.00,),
                      Position(ra=10. + 5 / 3600., dec=0.,
                                 ra_err=20 / 3600., dec_err=1.00,)]

        # Same as pair4 but with error increased 10-fold
        self.pair5 = [posn._replace(ra_err=posn.ra_err * 10, dec_err=posn.dec_err * 10)
                      for posn in self.pair4]

        # More basic meridian testing:
        # RA 1,359
        self.pair6 = [Position(ra=1, dec=0,
                               ra_err=1 , dec_err=1),
                     Position(ra=359.0 , dec=0,
                              ra_err=1, dec_err=1), ]
        #Is RA -1 same as RA 359?
        # RA 1,-1
        self.pair7 = copy(self.pair6)
        self.pair7[1] = self.pair7[1]._replace(ra=-1)

        # And when we cycle by 180?
        # RA 181, 539
        self.pair8 = [posn._replace(ra=posn.ra + 180) for posn in self.pair6]
        # RA 181, 179
        self.pair9 = [posn._replace(ra=posn.ra + 180) for posn in self.pair7]

        self.all_pairs = [self.pair1,
                          self.pair2,
                          self.pair3,
                          self.pair4,
                          self.pair5,
                          self.pair6,
                          self.pair7,
                          self.pair8,
                          self.pair9,
                          ]

    def test_python_formulae(self):
        """
        Test that the python version satisfies basic sanity checks. 
        
        This is a good place to start, being easiest to implement 
        and understand. We can then use it as a reference implementation.
        """

#         print "\n****"
#         for i, p in enumerate(self.all_pairs):
#             print "Pair", i, p
#             print "DR", py_deruiter(p[0], p[1])
#
#         print "\n****"


        # Ok, check we get the same results when we rotate RA by 270
        self.assertAlmostEqual(py_dr(self.pair1), py_dr(self.pair2))

        # And cycle one RA value by 360
        self.assertAlmostEqual(py_dr(self.pair1), py_dr(self.pair3))
        
        # R5 has 10 times error, -> 10 times smaller DR
        self.assertAlmostEqual(py_dr(self.pair4), 10 * py_dr(self.pair5))
        
        # OK meridian testing, e.g. RA 1, 359
        # RA 359 == RA -1 ?
        self.assertAlmostEqual(py_dr(self.pair6), py_dr(self.pair7))
        # Cycle by +180, all OK?
        # RA 181, 539
        self.assertAlmostEqual(py_dr(self.pair6), py_dr(self.pair8))
        # RA 179,181
        self.assertAlmostEqual(py_dr(self.pair6), py_dr(self.pair9))
        
        #Sanity check that it's commutative
        #(Something would have to be pretty wrong if this were not the 
        # case, but you never know)
        for test_pair in self.all_pairs:
            reversed = (test_pair[1], test_pair[0])
            self.assertEqual(py_dr(test_pair), py_dr(reversed))


    def test_sql_formulae(self):
        for pair in self.all_pairs:
            py_result = py_dr(pair)
            cm = py_cross_meridian_predicate(pair[0].ra, pair[1].ra)
            db_result = db_deruiter(self.conn, pair[0], pair[1], cm)
            db_result_rev = db_deruiter(self.conn, pair[1], pair[0], cm)
#             print "\nPAIR:", pair
#             print "PY, DB: ", py_result, db_result
            self.assertAlmostEqual(py_result, db_result, places=5)
            self.assertEqual(db_result, db_result_rev)

#     def test_basic_interface(self):
#         p1 = Position(ra=0, dec=0, ra_err=0.01, dec_err=0.01)
#         print
#         print "Result:", result
#         self.assertEqual(result, -2)

    def TestFullSequence(self):
        """
        Try the full works, from source insertion --> association.

        This confirms that all unit conversions are performed correctly,
        providing a final consistency check between our simple python version
        and the full SQL logic chain.
        """

        def test(pair_of_positions):
            pair = pair_of_positions
            dataset = DataSet(data={'description':"DeRuiter:" + self._testMethodName})
            n_images = 2
            #Set a massive beam as this places upper limit on assocs otherwise
            im_params = db_subs.example_dbimage_datasets(n_images,
                          beam_smaj_pix=float(1000),
                          beam_smin_pix=float(1000),
                             centre_ra=pair[0].ra,
                             centre_decl=pair[0].dec,
                             xtr_radius=3)


            # Note ra / ra_fit_err are in degrees.
            # ra_sys_err is in arcseconds, but we set it = 0 so doesn't matter.
            # ra_fit_err cannot be zero or we get div by zero errors.

            # On a side note there is a hard limit on association radii
            # (or specifically, the association candidates) set by the beam-size.
            # But for the current dummy images the beam-size is set huge,
            # so it doesn't matter.


            srcs = [position_to_extractedsource(p) for p in pair]
            python_dr = py_deruiter(pair[0], pair[1])
    #        print "Expected DR", python_dr

            for idx in [0, 1]:
                image = tkp.db.Image(dataset=dataset,
                                    data=im_params[idx])
                image.insert_extracted_sources([srcs[idx]])
                # Peform very loose association since we just want to store DR value.
                associate_extracted_sources(image.id, deRuiter_r=1e10)
            runcat = columns_from_table('runningcatalog', ['id'],
                                       where={'dataset':dataset.id})
#             print "\nTest Pair:", pair
#             print "***\nRESULTS:", runcat, "\n*****"
            self.assertEqual(len(runcat), 1)
            assoc = columns_from_table('assocxtrsource', ['r'],
                                       where={'runcat':runcat[0]['id']})
    #        print "Got assocs:", assoc
            self.assertEqual(len(assoc), 2)
            db_dr  = assoc[1]['r']
#             print "Results:", db_dr, python_dr
            self.assertAlmostEqual(db_dr, python_dr, places=4)


        # See issue 4774
        # https://support.astron.nl/lofar_issuetracker/issues/4774
        currently_working_test_cases = [self.pair1,
                          self.pair2,
#                           self.pair3,
                          self.pair4,
                          self.pair5,
                          self.pair6,
                          self.pair7,
#                           self.pair8,
                          self.pair9,
                          ]

#         for pair in self.all_pairs:
        for pair in currently_working_test_cases:
            test(pair)
