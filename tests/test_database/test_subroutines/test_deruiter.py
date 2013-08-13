import math

import unittest2 as unittest

import tkp.db
from tkp.testutil.decorators import requires_database
from tkp.testutil.db_queries import convert_to_cartesian as db_cartesian
from tkp.testutil import db_subs
from tkp.db.associations import associate_extracted_sources
from tkp.testutil.db_queries import (Position,
                                     extractedsource_to_position,
                                     position_to_extractedsource)
from tkp.testutil.db_queries import deruiter as db_deruiter
from tkp.testutil.calculations import deruiter_current as py_deruiter
from tkp.testutil.calculations import deruiter as py_deruiter_correct
from tkp.db.orm import DataSet
from tkp.db.generic import columns_from_table


@requires_database()
class TestDeruiter(unittest.TestCase):
    def setUp(self):
        self.db = tkp.db.Database()
        self.conn = self.db.connection


        self.pair1 = (Position(ra=5, dec=45, 
                               ra_err=5/3600., dec_err=5/3600.),
                     Position(ra=5+3/3600., dec=45+3/3600., 
                              ra_err=5/3600., dec_err=5/3600.),)
        self.pair2 = (self.pair1[0]._replace(ra=self.pair1[0].ra + 270),
                     self.pair1[1]._replace(ra=self.pair1[1].ra + 270),)
        
        self.pair3 = (Position(ra=10., dec=0.,
                                ra_err=20 / 3600., dec_err=1.00,),
                      Position(ra=10. + 5 / 3600., dec=0.,
                                 ra_err=20 / 3600., dec_err=1.00,))

        self.all_pairs = [self.pair1,
                          self.pair2,
                          self.pair3,
                          ]

    def test_python_formulae(self):
        """
        Test that the python version satisfies basic sanity checks. 
        
        This is a good place to start, being easiest to implement 
        and understand. We can then use it as a reference implementation.
        """
        print "Current"
        print "DR1", py_deruiter(self.pair1[0], self.pair1[1])
        print "DR2", py_deruiter(self.pair2[0], self.pair2[1])
        print "Uh oh!"

        print "Fixed"
        print "DR1", py_deruiter_correct(self.pair1[0], self.pair1[1])
        print "DR2", py_deruiter_correct(self.pair2[0], self.pair2[1])


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
            print "\nTest Pair:", pair
            dataset = DataSet(data={'description':"DeRuiter:" + self._testMethodName})
            n_images = 2
            im_params = db_subs.example_dbimage_datasets(n_images, centre_ra=10,
                                                         centre_decl=0)


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
                associate_extracted_sources(image.id, deRuiter_r=100)
            runcat = columns_from_table('runningcatalog', ['id'],
                                       where={'dataset':dataset.id})
    #        print "***\nRESULTS:", runcat, "\n*****"
            self.assertEqual(len(runcat), 1)
            assoc = columns_from_table('assocxtrsource', ['r'],
                                       where={'runcat':runcat[0]['id']})
    #        print "Got assocs:", assoc
            self.assertEqual(len(assoc), 2)
            db_dr  = assoc[1]['r']
            print "Results:", db_dr, python_dr
            self.assertAlmostEqual(db_dr, python_dr, places=4)
        for pair in self.all_pairs:
            test(pair)
