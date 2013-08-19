import math

import unittest2 as unittest

import tkp.db
import tkp.db.general as dbgen
from tkp.db.orm import DataSet
from tkp.db.associations import associate_extracted_sources
import tkp.db.associations as assoc_subs
from tkp.db.generic import columns_from_table, get_db_rows_as_dicts
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database
from tkp.testutil.calculations import deruiter as py_deruiter
from tkp.testutil.db_queries import extractedsource_to_position



@requires_database()
class TestOne2One(unittest.TestCase):
    """
    These tests will check the 1-to-1 source associations, i.e. an extractedsource
    has exactly one counterpart in the runningcatalog
    """
    def shortDescription(self):
        """http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/"""
        return None

    def tearDown(self):
        tkp.db.rollback()

    def test_one2one(self):
        dataset = DataSet(data={'description': 'assoc test set: 1-1'})
        n_images = 8
        im_params = db_subs.example_dbimage_datasets(n_images)

        steady_srcs = []
        n_steady_srcs = 3
        for i in range(n_steady_srcs):
            src = db_subs.example_extractedsource_tuple()
            src = src._replace(ra=src.ra + 2 * i)
            steady_srcs.append(src)

        for im in im_params:
            image = tkp.db.Image(dataset=dataset, data=im)
            dbgen.insert_extracted_sources(image.id, steady_srcs, 'blind')
            associate_extracted_sources(image.id, deRuiter_r = 3.717)

        # Check runningcatalog, runningcatalog_flux, assocxtrsource.
        # note that the order of insertions is not garanteed, so we ORDER by
        # wm_RA
        query = """\
        SELECT datapoints
              ,wm_ra
              ,wm_decl
              ,wm_ra_err
              ,wm_decl_err
              ,x
              ,y
              ,z
          FROM runningcatalog
         WHERE dataset = %s
        ORDER BY wm_ra
        """
        cursor = tkp.db.execute(query, (dataset.id,))
        runcat = zip(*cursor.fetchall())
        self.assertNotEqual(len(runcat), 0)
        dp = runcat[0]
        wm_ra = runcat[1]
        wm_decl = runcat[2]
        wm_ra_err = runcat[3]
        wm_decl_err = runcat[4]
        x = runcat[5]
        y = runcat[6]
        z = runcat[7]
        # Check for 1 entry in runcat
        self.assertEqual(len(dp), len(steady_srcs))
        self.assertEqual(dp[0], n_images)
        self.assertAlmostEqual(wm_ra[0], steady_srcs[0].ra)
        self.assertAlmostEqual(wm_decl[0], steady_srcs[0].dec)
        self.assertAlmostEqual(wm_ra_err[0], math.sqrt(
                           1./ (n_images / ( (steady_srcs[0].ra_fit_err*3600.)**2 + (steady_srcs[0].ra_sys_err)**2))
                               ))
        self.assertAlmostEqual(wm_decl_err[0], math.sqrt(
                           1./ (n_images / ((steady_srcs[0].dec_fit_err*3600.)**2 + (steady_srcs[0].dec_sys_err)**2 ))
                               ))

        self.assertAlmostEqual(x[0],
                    math.cos(math.radians(steady_srcs[0].dec))*
                        math.cos(math.radians(steady_srcs[0].ra)))
        self.assertAlmostEqual(y[0],
                   math.cos(math.radians(steady_srcs[0].dec))*
                        math.sin(math.radians(steady_srcs[0].ra)))
        self.assertAlmostEqual(z[0], math.sin(math.radians(steady_srcs[0].dec)))

        # Check that xtrsrc ids in assocxtrsource are the ones from extractedsource
        query ="""\
        SELECT a.runcat
              ,a.xtrsrc
          FROM assocxtrsource a
              ,runningcatalog r
         WHERE a.runcat = r.id
           AND r.dataset = %s
        ORDER BY a.xtrsrc
        """
        cursor = tkp.db.execute(query, (dataset.id,))
        assoc = zip(*cursor.fetchall())
        self.assertNotEqual(len(assoc), 0)
        aruncat = assoc[0]
        axtrsrc = assoc[1]
        self.assertEqual(len(axtrsrc), n_images * n_steady_srcs)

        query = """\
        SELECT x.id
          FROM extractedsource x
              ,image i
         WHERE x.image = i.id
           AND i.dataset = %s
        ORDER BY x.id
        """
        cursor = tkp.db.execute(query, (dataset.id,))
        xtrsrcs = zip(*cursor.fetchall())
        self.assertNotEqual(len(xtrsrcs), 0)
        xtrsrc = xtrsrcs[0]
        self.assertEqual(len(xtrsrc), n_images * n_steady_srcs)

        for i in range(len(xtrsrc)):
            self.assertEqual(axtrsrc[i], xtrsrc[i])

        # Check runcat_fluxes
        query = """\
        SELECT rf.band
              ,rf.stokes
              ,rf.f_datapoints
              ,rf.avg_f_peak
              ,rf.avg_f_peak_weight
              ,rf.avg_f_int
              ,rf.avg_f_int_weight
          FROM runningcatalog_flux rf
              ,runningcatalog r
         WHERE r.id = rf.runcat
           AND r.dataset = %s
        """
        cursor = tkp.db.execute(query, (dataset.id,))
        fluxes = zip(*cursor.fetchall())
        self.assertNotEqual(len(fluxes), 0)
        f_datapoints = fluxes[2]
        avg_f_peak = fluxes[3]
        avg_f_peak_weight = fluxes[4]
        avg_f_int = fluxes[5]
        avg_f_int_weight = fluxes[6]
        self.assertEqual(len(f_datapoints), n_steady_srcs)
        self.assertEqual(f_datapoints[0], n_images)
        self.assertEqual(avg_f_peak[0], steady_srcs[0].peak)
        self.assertEqual(avg_f_peak_weight[0], 1./steady_srcs[0].peak_err**2)
        self.assertEqual(avg_f_int[0], steady_srcs[0].flux)
        self.assertEqual(avg_f_int_weight[0], 1./steady_srcs[0].flux_err**2)


@requires_database()
class TestMixedSkyregions(unittest.TestCase):
    """
    Tests that association and related calculations happen correctly when a
    source is seen in multiple skyregions.
    """
    def shortDescription(self):
        return None

    def tearDown(self):
        tkp.db.rollback()

    def TestSubZeroAvgWra(self):
        """
        Check that we properly take the modulus of avg_wra in cases where it
        falls below zero.

        See https://support.astron.nl/lofar_issuetracker/issues/4640 for
        details. The detailed numbers in this test (RA, dec, etc) come from
        the data involved in that bug report and have no other special
        meaning.
        """
        dataset = DataSet(data={'description': "Test:" + self._testMethodName})
        im_list = db_subs.example_dbimage_datasets(
            n_images=10, centre_ra=358.125, centre_decl=50.941028000000003, xtr_radius=1.38888888889
        )
        im_list.extend(
            db_subs.example_dbimage_datasets(
                n_images=1, centre_ra=354.375, centre_decl=50.941028000000003, xtr_radius=1.38888888889
            )
        )

        posns = [(356.33840829988583, 50.516),
                 (0.33840829988583, 50.516), ]
        sorted_src_ras = sorted([p[0] for p in posns])
        srcs = [db_subs.example_extractedsource_tuple(ra=p[0], dec=p[1]) for p
                in posns]

        for im in im_list:
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources(srcs)
            associate_extracted_sources(image.id, deRuiter_r=3.717)

            runcat = columns_from_table('runningcatalog', ['wm_ra'],
                where={'dataset': dataset.id}
            )
            self.assertEqual(len(runcat), 2)
            wm_ras = [ r['wm_ra'] for r in runcat]
#            print "WM_RA:", sorted(wm_ras)
            for known, calc in zip(sorted_src_ras, sorted(wm_ras)):
                self.assertAlmostEqual(known, calc)


    def TestCrossMeridian(self):
        """
        A source is observed in two skyregions: one which crosses the
        meridian, and one which does not. We check that the associated source
        has the correct weighted mean RA.

        See also #4497.
        """
        dataset = DataSet(data={'description': "Test:" + self._testMethodName})

        im_list = [
            db_subs.example_dbimage_datasets(
                n_images=1, centre_ra=0, centre_decl=0, xtr_radius=10
            )[0],
            db_subs.example_dbimage_datasets(
                n_images=1, centre_ra=0, centre_decl=0, xtr_radius=10
            )[0],
            db_subs.example_dbimage_datasets(
                n_images=1, centre_ra=15, centre_decl=0, xtr_radius=10
            )[0],
            db_subs.example_dbimage_datasets(
                n_images=1, centre_ra=15, centre_decl=0, xtr_radius=10
            )[0],
        ]

        source_ra = 7.5
        src = db_subs.example_extractedsource_tuple(ra=source_ra, dec=0)

        for im in im_list:
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources([src])
            associate_extracted_sources(image.id, deRuiter_r=3.717)

        runcat = columns_from_table('runningcatalog', ['wm_ra'],
            where={'dataset': dataset.id}
        )
        self.assertAlmostEqual(runcat[0]['wm_ra'], source_ra)


#@unittest.skip
@requires_database()
class TestMeridianOne2One(unittest.TestCase):
    """
    These tests will check the 1-to-1 source associations, i.e. an extractedsource
    has exactly one counterpart in the runningcatalog
    """
    def shortDescription(self):
        return None

    def tearDown(self):
        tkp.db.rollback()

    def TestMeridianCrossLowHighEdgeCase(self):
        """What happens if a source is right on the meridian?"""

        dataset = DataSet(data={'description':"Assoc 1-to-1:" + self._testMethodName})
        n_images = 3
        im_params = db_subs.example_dbimage_datasets(n_images, centre_ra=0.5,
                                                      centre_decl=10)
        src_list = []
        src0 = db_subs.example_extractedsource_tuple(ra=0.0001, dec=10.5,
                                             ra_fit_err=0.01, dec_fit_err=0.01)
        src_list.append(src0)
        src1 = src0._replace(ra=0.0003)
        src_list.append(src1)
        src2 = src0._replace(ra=359.9999)
        src_list.append(src2)

        for idx, im in enumerate(im_params):
            im['centre_ra'] = 359.9
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources([src_list[idx]])
            associate_extracted_sources(image.id, deRuiter_r=3.717)
        runcat = columns_from_table('runningcatalog', ['datapoints', 'wm_ra'],
                                   where={'dataset':dataset.id})
#        print "***\nRESULTS:", runcat, "\n*****"
        self.assertEqual(len(runcat), 1)
        self.assertEqual(runcat[0]['datapoints'], 3)
        avg_ra = ((src0.ra+180)%360 + (src1.ra+180)%360 + (src2.ra+180)%360)/3 - 180
        self.assertAlmostEqual(runcat[0]['wm_ra'], avg_ra)

    def TestMeridianCrossHighLowEdgeCase(self):
        """What happens if a source is right on the meridian?"""

        dataset = DataSet(data={'description':"Assoc 1-to-1:" + self._testMethodName})
        n_images = 3
        im_params = db_subs.example_dbimage_datasets(n_images, centre_ra=0.5,
                                                      centre_decl=10)
        src_list = []
        src0 = db_subs.example_extractedsource_tuple(ra=359.9999, dec=10.5,
                                             ra_fit_err=0.01, dec_fit_err=0.01)
        src_list.append(src0)
        src1 = src0._replace(ra=0.0003)
        src_list.append(src1)
        src2 = src0._replace(ra=0.0001)
        src_list.append(src2)

        for idx, im in enumerate(im_params):
            im['centre_ra'] = 359.9
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources([src_list[idx]])
            associate_extracted_sources(image.id, deRuiter_r=3.717)
        runcat = columns_from_table(
                                   'runningcatalog', ['datapoints', 'wm_ra'],
                                   where={'dataset':dataset.id})
#        print "***\nRESULTS:", runcat, "\n*****"
        self.assertEqual(len(runcat), 1)
        self.assertEqual(runcat[0]['datapoints'], 3)
        avg_ra = ((src0.ra+180)%360 + (src1.ra+180)%360 + (src2.ra+180)%360)/3 - 180
        self.assertAlmostEqual(runcat[0]['wm_ra'], avg_ra)

    def TestMeridianHigherEdgeCase(self):
        """What happens if a source is right on the meridian?"""

        dataset = DataSet(data={'description':"Assoc 1-to-1:" + self._testMethodName})
        n_images = 3
        im_params = db_subs.example_dbimage_datasets(n_images, centre_ra=0.5,
                                                      centre_decl=10)
        src_list = []
        src0 = db_subs.example_extractedsource_tuple(ra=359.9983, dec=10.5,
                                             ra_fit_err=0.01, dec_fit_err=0.01)
        src_list.append(src0)
        src1 = src0._replace(ra=359.9986)
        src_list.append(src1)
        src2 = src0._replace(ra=359.9989)
        src_list.append(src2)

        for idx, im in enumerate(im_params):
            im['centre_ra'] = 359.9
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources([src_list[idx]])
            associate_extracted_sources(image.id, deRuiter_r=3.717)
        runcat = columns_from_table('runningcatalog', ['datapoints', 'wm_ra'],
                                   where={'dataset':dataset.id})
#        print "***\nRESULTS:", runcat, "\n*****"
        self.assertEqual(len(runcat), 1)
        self.assertEqual(runcat[0]['datapoints'], 3)
        avg_ra = (src0.ra + src1.ra +src2.ra)/3
        self.assertAlmostEqual(runcat[0]['wm_ra'], avg_ra)

    def TestMeridianLowerEdgeCase(self):
        """What happens if a source is right on the meridian?"""

        dataset = DataSet(data={'description':"Assoc 1-to-1:" +
                                self._testMethodName})
        n_images = 3
        im_params = db_subs.example_dbimage_datasets(n_images, centre_ra=0.5,
                                                      centre_decl=10)
        src_list = []
        src0 = db_subs.example_extractedsource_tuple(ra=0.0002, dec=10.5,
                                             ra_fit_err=0.01, dec_fit_err=0.01)
        src_list.append(src0)
        src1 = src0._replace(ra=0.0003)
        src_list.append(src1)
        src2 = src0._replace(ra=0.0004)
        src_list.append(src2)

        for idx, im in enumerate(im_params):
            im['centre_ra'] = 359.9
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources([src_list[idx]])
            associate_extracted_sources(image.id, deRuiter_r=3.717)
        runcat = columns_from_table('runningcatalog', ['datapoints', 'wm_ra'],
                                   where={'dataset':dataset.id})
#        print "***\nRESULTS:", runcat, "\n*****"
        self.assertEqual(len(runcat), 1)
        self.assertEqual(runcat[0]['datapoints'], 3)
        avg_ra = (src0.ra + src1.ra +src2.ra)/3
        self.assertAlmostEqual(runcat[0]['wm_ra'], avg_ra)




class TestOne2Many(unittest.TestCase):
    """
    These tests will check the 1-to-many source associations, i.e. two extractedsources
    have the same one counterpart in the runningcatalog
    """
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        tkp.db.rollback()

    def test_one2many(self):
        dataset = DataSet(data={'description': 'assoc test set: 1-n'})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkp.db.Image(dataset=dataset, data=im_params[0])
        imageid1 = image.id
        src = []
        # 1 source
        src.append(db_subs.example_extractedsource_tuple(ra=123.1235, dec=10.55,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ra_sys_err=20, dec_sys_err=20
                                                        ))
        results = []
        results.append(src[-1])
        dbgen.insert_extracted_sources(imageid1, results, 'blind')
        associate_extracted_sources(imageid1, deRuiter_r = 3.717)

        query = """\
        SELECT id
          FROM extractedsource
         WHERE image = %s
        """
        self.database.cursor.execute(query, (imageid1,))
        im1 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(im1), 0)
        im1src1 = im1[0]
        self.assertEqual(len(im1src1), 1)

        query = """\
        SELECT id
              ,xtrsrc
          FROM runningcatalog
         WHERE dataset = %s
        """
        self.database.cursor.execute(query, (dataset.id,))
        rc1 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(rc1), 0)
        runcat1 = rc1[0]
        xtrsrc1 = rc1[1]
        self.assertEqual(len(runcat1), len(src))
        self.assertEqual(xtrsrc1[0], im1src1[0])

        query = """\
        SELECT a.runcat
              ,a.xtrsrc
              ,a.type
          FROM assocxtrsource a
              ,runningcatalog r
         WHERE a.runcat = r.id
           AND r.dataset = %s
        """
        self.database.cursor.execute(query, (dataset.id,))
        assoc1 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(assoc1), 0)
        aruncat1 = assoc1[0]
        axtrsrc1 = assoc1[1]
        atype = assoc1[2]
        self.assertEqual(len(aruncat1), len(src))
        self.assertEqual(axtrsrc1[0], im1src1[0])
        self.assertEqual(axtrsrc1[0], xtrsrc1[0])
        self.assertEqual(atype[0], 4)
        #TODO: Add runcat_flux test

        # image 2
        image = tkp.db.Image(dataset=dataset, data=im_params[1])
        imageid2 = image.id
        src = []
        # 2 sources (located close to source 1, catching the 1-to-many case
        src.append(db_subs.example_extractedsource_tuple(ra=123.12349, dec=10.549,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ra_sys_err=20, dec_sys_err=20
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.12351, dec=10.551,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ra_sys_err=20, dec_sys_err=20
                                                        ))
        results = []
        results.append(src[0])
        results.append(src[1])
        dbgen.insert_extracted_sources(imageid2, results, 'blind')
        associate_extracted_sources(imageid2, deRuiter_r = 3.717)

        query = """\
        SELECT id
          FROM extractedsource
         WHERE image = %s
        ORDER BY id
        """
        self.database.cursor.execute(query, (imageid2,))
        im2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(im2), 0)
        im2src = im2[0]
        self.assertEqual(len(im2src), len(src))

        query = """\
        SELECT r.id
              ,r.xtrsrc
              ,x.image
              ,r.datapoints
              ,r.wm_ra
              ,r.wm_decl
              ,r.wm_ra_err
              ,r.wm_decl_err
          FROM runningcatalog r
              ,extractedsource x
         WHERE r.xtrsrc = x.id
           AND dataset = %s
        ORDER BY r.id
        """
        self.database.cursor.execute(query, (dataset.id,))
        rc2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(rc2), 0)
        runcat2 = rc2[0]
        xtrsrc2 = rc2[1]
        image2 = rc2[2]
        self.assertEqual(len(runcat2), len(src))
        self.assertNotEqual(xtrsrc2[0], xtrsrc2[1])
        self.assertEqual(image2[0], image2[1])
        self.assertEqual(image2[0], imageid2)

        query = """\
        SELECT a.runcat
              ,a.xtrsrc
              ,a.type
              ,x.image
          FROM assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
         WHERE a.runcat = r.id
           AND a.xtrsrc = x.id
           AND r.dataset = %s
        ORDER BY a.xtrsrc
                ,a.runcat
        """
        self.database.cursor.execute(query, (dataset.id,))
        assoc2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(assoc2), 0)
        aruncat2 = assoc2[0]
        axtrsrc2 = assoc2[1]
        atype2 = assoc2[2]
        aimage2 = assoc2[3]
        self.assertEqual(len(aruncat2), 2*len(src))
        self.assertEqual(axtrsrc2[0], im1src1[0])
        self.assertEqual(axtrsrc2[1], im1src1[0])
        self.assertNotEqual(axtrsrc2[2], axtrsrc2[3])
        self.assertEqual(aimage2[2], aimage2[3])
        self.assertEqual(aimage2[2], imageid2)
        self.assertEqual(atype2[0], 6)
        self.assertEqual(atype2[1], 6)
        self.assertEqual(atype2[2], 2)
        self.assertEqual(atype2[3], 2)
        self.assertEqual(aruncat2[0], runcat2[0])
        self.assertEqual(aruncat2[1], runcat2[1])

        query = """\
        SELECT COUNT(*)
          FROM runningcatalog
         WHERE dataset = %s
           AND xtrsrc IN (SELECT id
                            FROM extractedsource
                           WHERE image = %s
                         )
        """
        self.database.cursor.execute(query, (dataset.id, imageid1))
        count = zip(*self.database.cursor.fetchall())
        self.assertEqual(count[0][0], 0)

        #TODO: Add runcat_flux test


class TestMany2One(unittest.TestCase):
    """
    These tests will check the many-to-1 source associations, i.e. one extractedsource
    that has two (or more) counterparts in the runningcatalog.

    """
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        tkp.db.rollback()

    def test_many2one(self):
        dataset = DataSet(data={'description': 'assoc test set: n-1'})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkp.db.Image(dataset=dataset, data=im_params[0])
        imageid1 = image.id
        src = []
        # 2 sources (located close together, so the catching the many-to-1 case in next image
        src.append(db_subs.example_extractedsource_tuple(ra=122.985, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ra_sys_err=20, dec_sys_err=20
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.015, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ra_sys_err=20, dec_sys_err=20
                                                        ))
        results = []
        results.append(src[0])
        results.append(src[1])
        dbgen.insert_extracted_sources(imageid1, results, 'blind')
        associate_extracted_sources(imageid1, deRuiter_r = 3.717)

        query = """\
        SELECT id
          FROM extractedsource
         WHERE image = %s
        ORDER BY id
        """
        self.database.cursor.execute(query, (imageid1,))
        im1 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(im1), 0)
        im1src = im1[0]
        self.assertEqual(len(im1src), len(src))

        # image 2
        image = tkp.db.Image(dataset=dataset, data=im_params[1])
        imageid2 = image.id
        src = []
        # 1 source
        src.append(db_subs.example_extractedsource_tuple(ra=123.0, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ra_sys_err=20, dec_sys_err=20
                                                        ))
        results = []
        results.append(src[-1])
        dbgen.insert_extracted_sources(imageid2, results, 'blind')
        associate_extracted_sources(imageid2, deRuiter_r = 3.717)

        query = """\
        SELECT id
          FROM extractedsource
         WHERE image = %s
        """
        self.database.cursor.execute(query, (imageid2,))
        im2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(im2), 0)
        im2src = im2[0]
        self.assertEqual(len(im2src), 1)

        query = """\
        SELECT id
              ,xtrsrc
              ,datapoints
          FROM runningcatalog
         WHERE dataset = %s
        ORDER BY xtrsrc
        """
        self.database.cursor.execute(query, (dataset.id,))
        rc2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(rc2), 0)
        runcat2 = rc2[0]
        xtrsrc2 = rc2[1]
        datapoints = rc2[2]
        self.assertEqual(len(runcat2), 2)
        self.assertEqual(xtrsrc2[0], im1src[0])
        self.assertEqual(xtrsrc2[1], im1src[1])
        self.assertEqual(datapoints[0], datapoints[1])
        self.assertEqual(datapoints[0], 2)

        query = """\
        SELECT a.runcat
              ,r.xtrsrc as rxtrsrc
              ,a.xtrsrc as axtrsrc
              ,a.type
              ,x.image
          FROM assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
         WHERE a.runcat = r.id
           AND a.xtrsrc = x.id
           AND r.dataset = %s
        ORDER BY r.xtrsrc
                ,a.xtrsrc
        """
        self.database.cursor.execute(query, (dataset.id,))
        assoc2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(assoc2), 0)
        aruncat2 = assoc2[0]
        rxtrsrc2 = assoc2[1]
        axtrsrc2 = assoc2[2]
        atype2 = assoc2[3]
        aimage2 = assoc2[4]
        self.assertEqual(len(aruncat2), 4)
        # We can't tell/predict the order of insertion of the runcat entries,
        # but we can for the xtrsrc of the runcat-xtrsrc pair.
        #self.assertEqual(aruncat2[0], aruncat2[2])
        #self.assertEqual(aruncat2[1], aruncat2[3])
        self.assertEqual(rxtrsrc2[0], rxtrsrc2[1])
        self.assertEqual(rxtrsrc2[2], rxtrsrc2[3])
        self.assertEqual(rxtrsrc2[0], axtrsrc2[0])
        self.assertEqual(rxtrsrc2[1], axtrsrc2[1] - 2)
        self.assertEqual(rxtrsrc2[2], axtrsrc2[2])
        self.assertEqual(rxtrsrc2[3], axtrsrc2[3] - 1)
        self.assertEqual(axtrsrc2[0], im1src[0])
        self.assertEqual(axtrsrc2[1], im2src[0])
        self.assertEqual(axtrsrc2[2], im1src[1])
        self.assertEqual(axtrsrc2[3], im2src[0])
        self.assertEqual(atype2[0], 4)
        self.assertEqual(atype2[1], 3)
        self.assertEqual(atype2[2], 4)
        self.assertEqual(atype2[3], 3)
        self.assertEqual(aimage2[0], imageid1)
        self.assertEqual(aimage2[1], imageid2)
        self.assertEqual(aimage2[2], imageid1)
        self.assertEqual(aimage2[3], imageid2)
        #TODO: Add runcat_flux test


class TestMany2Many(unittest.TestCase):
    """
    These tests will check the many-to-many source associations, i.e. many extractedsources
    that has two (or more) counterparts in the runningcatalog.

    """
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        tkp.db.rollback()

    def test_many2many(self):
        """
        This test sets up two images with a pair of sources in each.
        All sources are close to the RA,Dec position (123,10).
        In the first image they equidistant in RA, in the second in Dec.
        
        For the second pair, we then test different sub-cases where
        each source may get a minute bump towards one of the earlier sources
        (so slight RA change). This has the effect of making the DR 
        radius non-equal, which changes how the association candidates get
        rejected / accepted.
        
        Note that currently, if the DR radii are exactly equal on all
        4 sides of the rhombus, then pruning does not happen, we get
        many-to-many associations remaining, and break the SQL constraints.
        (See issue: 
        https://support.astron.nl/lofar_issuetracker/issues/4778 )
        """

        def test_source_pairs(im_params, image1_srcs, image2_srcs):
            """
            Load 2 images in the database according to im_params,
            then populate with image1_srcs / image2_srcs accordingly.
            Associate. 
            
            Return dicts representing relevant runcat, assoc, and extractedsource
            entries.
            """
            src1 = image1_srcs
            src2 = image2_srcs
        # Check that we have chosen sufficiently close sources /
        # suff. large errors / suff. large DR to allow cross-association
            for src_pair in [(src1[0], src2[0]),
                         (src1[0], src2[1]),
                         (src1[1], src2[0]),
                         (src1[1], src2[1]),
                         ]:
                dr_between_srcs = py_deruiter(extractedsource_to_position(src_pair[0]),
                                          extractedsource_to_position(src_pair[1]))
        #        print "\nDR between: ", dr_between_srcs
                self.assertTrue(dr_limit > dr_between_srcs)
            
            dataset = DataSet(data={'description': 'assoc test set: n-m'})
            image1 = tkp.db.Image(dataset=dataset, data=im_params[0])
            image2 = tkp.db.Image(dataset=dataset, data=im_params[1])

            dbgen.insert_extracted_sources(image1.id, src1, 'blind')
            associate_extracted_sources(image1.id, deRuiter_r=dr_limit)

            dbgen.insert_extracted_sources(image2.id, src2, 'blind')

    #         Double check that we actually get many-to-many candidate links:
            assoc_subs._insert_temprunningcatalog(image2.id, dr_limit,
                                            assoc_subs._check_meridian_wrap(image2.id))
            candidate_assocs = columns_from_table('temprunningcatalog')
            self.assertEqual(len(candidate_assocs), 4)

            # Now do the proper association
            associate_extracted_sources(image2.id, deRuiter_r=dr_limit)


            runcat = columns_from_table('runningcatalog',
                                                 where={'dataset':dataset.id},
                                                 order='xtrsrc')

            # Grab all associations for this dataset
            query = """\
            SELECT assoc.runcat
                  ,rc.xtrsrc as rxtrsrc
                  ,assoc.xtrsrc as extraction_id
                  ,assoc.type
                  ,ex.image
                  ,ex.ra
                  ,ex.decl
              FROM assocxtrsource assoc
                  ,runningcatalog rc
                  ,extractedsource ex
             WHERE assoc.runcat = rc.id
               AND assoc.xtrsrc = ex.id
               AND rc.dataset = %s
            ORDER BY rc.xtrsrc
                    ,assoc.xtrsrc
            """
            cursor = tkp.db.execute(query, (dataset.id,), commit=False)
            associations = get_db_rows_as_dicts(cursor)

            # Whaddya ya got?
            extracted = columns_from_table('extractedsource',
                                           where={'image':image1.id})
            extracted.extend(columns_from_table('extractedsource',
                                           where={'image':image2.id}))
            for rc_entry in runcat:
                associated_srcs = []
                for a in associations:
                    if a['runcat'] == rc_entry['id']:
                        associated_srcs.append(a)
                rc_entry['assoc'] = associated_srcs
            return runcat, extracted

        def summarise_associations(runcat, extracted):
            """Print a nice summary of the results"""

            print "\nSources input:"
            for ex in sorted(extracted, key=lambda x:x['image']):
                print ', '.join(kw + ':' + str(ex[kw]) for kw in
                                 ('image', 'id', 'ra', 'decl'))

            print "\nResulting associations"
            for rc_entry in sorted(runcat, key=lambda x:x['id']):
                print ', '.join(kw + ':' + str(rc_entry[kw]) for kw in
                                ('id', 'wm_ra', 'wm_decl', 'datapoints', 'inactive'))
                for assoc_entry in sorted(rc_entry['assoc'], key=lambda x:x['image']):
                    print '\t', assoc_entry
            print
    #         self.assertEqual(len(runcat), 2)
            for entry in runcat:
                self.assertEqual(entry['datapoints'], 2)

        # Ok, now the main event:

        n_images = 2
        src_offset_deg = 20 / 3600.
        tiny_offset_deg = 1 / 3600.  # 1 arcsecond
        pos_err_deg = 30 / 3600.
        dr_limit = 3.717

        im_params = db_subs.example_dbimage_datasets(n_images,
                                                     centre_ra=123,
                                                     centre_decl=10
                                                     )
        # We set a huge beam size as that can limit candidate assocs otherwise.
        template_source = db_subs.example_extractedsource_tuple(ra=123, dec=10.5,
                             ra_fit_err=pos_err_deg, dec_fit_err=pos_err_deg,
                             beam_maj=100, beam_min=100, beam_angle=45,
                             ra_sys_err=0, dec_sys_err=0
                             )
        base_srcs = []
        # 2 sources (located relatively close together, allowing for possible
        # multiple associations)
        base_srcs.append(template_source._replace(ra=template_source.ra - src_offset_deg))
        base_srcs.append(template_source._replace(ra=template_source.ra + src_offset_deg))

        p2_both_offset = []
        # 2 sources, where both can be associated with both from image 1
        # Second source is slightly bumped towards positive RA to separate DR values.
        p2_both_offset.append(template_source._replace(
                                  ra=template_source.ra - tiny_offset_deg,
                                  dec=template_source.dec - src_offset_deg))
        p2_both_offset.append(template_source._replace(
                                  ra=template_source.ra + tiny_offset_deg,
                                     dec=template_source.dec + src_offset_deg))

        p2_only_second_offset = []
        p2_only_second_offset.append(
                template_source._replace(ra=template_source.ra,
                                         dec=template_source.dec - src_offset_deg))
        p2_only_second_offset.append(template_source._replace(
                              ra=template_source.ra + tiny_offset_deg,
                             dec=template_source.dec + src_offset_deg))

        # Danger Will Robinson, equilateral rhombus!
        p2_neither_offset = []
        p2_neither_offset.append(
                template_source._replace(ra=template_source.ra,
                                         dec=template_source.dec - src_offset_deg))
        p2_neither_offset.append(
                template_source._replace(ra=template_source.ra,
                                         dec=template_source.dec + src_offset_deg))


        both_offset_results = test_source_pairs(im_params,
                                                    base_srcs, p2_both_offset)
        single_offset_results = test_source_pairs(im_params,
                                            base_srcs, p2_only_second_offset)
#         neither_offset_results = test_source_pairs(im_params,
#                                             base_srcs, p2_neither_offset)

        for results in (both_offset_results, single_offset_results,
#                         neither_offset_results
                        ):
            summarise_associations(*results)

        # In the case that both secondary sources are offset,
        # both extractedsources have a preferred runcat,
        # and the other runcat-xtrsrc link is pruned
        runcat, extracted = both_offset_results
        self.assertEqual(len(runcat), 2)
        for rc in runcat:
            self.assertEqual(rc['datapoints'], 2)


        # We expect that the source nudged left ends up associated
        # with the left-hand base source, and vice versa:
        runcat_sorted_by_ra = sorted(runcat, key=lambda x:x['wm_ra'])
        for src in runcat_sorted_by_ra[0]['assoc']:
            self.assertTrue(src['ra'] < template_source.ra)
        for src in runcat_sorted_by_ra[1]['assoc']:
            self.assertTrue(src['ra'] > template_source.ra)
        

        # In the case that only a single secondary sources is offset,
        # only one extractedsource has a preferred runcat,
        # so only one link gets pruned.
        # As a result, the equidistant extracted source becomes part of a
        # many-to-one relation
        runcat, extracted = single_offset_results
        self.assertEqual(len(runcat), 3)

        offset_secondary_src_id=None
        for ex in extracted:
            if abs(ex['ra'] - p2_only_second_offset[1].ra) < 1e-5:
                offset_secondary_src_id = ex['id']
        print "OFFSET ID", offset_secondary_src_id
        # So, we only expect to see this ID once in the runningcatalog results:
        ex_ids_in_runcat = []
        for rc_entry in runcat:
            ex_ids_in_runcat.extend([a['extraction_id']
                                     for a in rc_entry['assoc']])
        print "EX IDS:", ex_ids_in_runcat
        self.assertEqual(ex_ids_in_runcat.count(offset_secondary_src_id), 1)

        # If neither secondary is offset: Boom!
        # https://support.astron.nl/lofar_issuetracker/issues/4778



