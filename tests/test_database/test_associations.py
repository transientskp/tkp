import math
import logging
from io import BytesIO

import unittest2 as unittest

import tkp.db
import tkp.db.general as dbgen
from tkp.db.orm import DataSet
import tkp.db.associations as assoc_subs
from tkp.db.associations import associate_extracted_sources
from tkp.db.generic import columns_from_table, get_db_rows_as_dicts
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database


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
              ,wm_uncertainty_ew
              ,wm_uncertainty_ns
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
        wm_uncertainty_ew = runcat[3]
        wm_uncertainty_ns = runcat[4]
        x = runcat[5]
        y = runcat[6]
        z = runcat[7]
        # Check for 1 entry in runcat
        self.assertEqual(len(dp), len(steady_srcs))
        self.assertEqual(dp[0], n_images)
        self.assertAlmostEqual(wm_ra[0], steady_srcs[0].ra)
        self.assertAlmostEqual(wm_decl[0], steady_srcs[0].dec)
        self.assertAlmostEqual(wm_uncertainty_ew[0], math.sqrt(
                           1./ (n_images / ( (steady_srcs[0].error_radius)**2 + (steady_srcs[0].ew_sys_err)**2))
                               ) / 3600)
        self.assertAlmostEqual(wm_uncertainty_ns[0], math.sqrt(
                           1./ (n_images / ((steady_srcs[0].error_radius)**2 + (steady_srcs[0].ns_sys_err)**2 ))
                               ) / 3600)

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


    def test_infinite_errors(self):
        # Check that source association doesn't choke on sources with infinite
        # errors. This is a problem because the calculation of the
        # dimensionless distance involves weighting by error radius, and hence
        # can cause underflow errors.
        dataset = DataSet(data={'description': 'test_infinite_errors'})
        im_params = db_subs.example_dbimage_datasets(2)

        extracted_source = db_subs.example_extractedsource_tuple(error_radius=float('inf'))

        for im_param in im_params:
            image = tkp.db.Image(dataset=dataset, data=im_param)
            image.insert_extracted_sources([extracted_source])
            # NB choice of De Ruiter radius is arbitrary.
            associate_extracted_sources(image.id, deRuiter_r=1.0)


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

    def TestNCP(self):
        """
        This simulates an NCP-like observation, where we point at a dec of +90
        and thereby include sources at a wide range of RAs.

        Developed for testing #4599.
        """
        dataset = DataSet(data={'description': "Test:" + self._testMethodName})

        # 4 images, all pointing at the NCP, with big extraction radii.
        im_list = db_subs.example_dbimage_datasets(
            n_images=4, centre_ra=0, centre_decl=90, xtr_radius=80
        )

        # Let's have one source near RA=0, the other near RA=180
        ras = [0.0, 0.1, 45.0, 90.0, 179.9, 180.0, 180.1, 270.0, 359.9]
        sources = [db_subs.example_extractedsource_tuple(ra=ra, dec=85) for ra in ras]

        for im in im_list:
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources(sources)
            associate_extracted_sources(image.id, deRuiter_r=3.717)

        runcat = columns_from_table('runningcatalog', ['wm_ra'],
            where={'dataset': dataset.id}
        )
        wm_ras = sorted(r['wm_ra'] for r in runcat)
        for ctr, ra in enumerate(ras):
            self.assertAlmostEqual(wm_ras[ctr], ra)


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

    def TestRoundingAroundZero(self):
        """
        If we have a source with an RA of exactly zero, the numerics in the
        association procedure will eventually allocate it a weighted mean RA
        which is infinitesimally less than zero (say, -d).

        If delta is sufficiently small, dynamic range constraints on floating
        point arithmetic means that -d+360==360. Therefore, when performing
        cross-meridian associations, we could end up with a source at the
        meaningless RA of 360.

        Here, we ensure this doesn't happen. See the discussion at issue
        #4599.
        """
        dataset = DataSet(data={'description':"Assoc rounding:" + self._testMethodName})

        im_list = db_subs.example_dbimage_datasets(
            n_images=5, centre_ra=0, centre_decl=0, xtr_radius=10
        )
        source = db_subs.example_extractedsource_tuple(ra=0.0, dec=0.0)
        for im in im_list:
            image = tkp.db.Image(dataset=dataset, data=im)
            image.insert_extracted_sources([source])
            associate_extracted_sources(image.id, deRuiter_r=3.717)

        runcat = columns_from_table('runningcatalog', ['wm_ra'],
            where={'dataset': dataset.id}
        )
        self.assertEqual(runcat[0]['wm_ra'], 0.0)


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
        """Checking that source measurements that flip around the 
        meridian are being associated.
        See TestNCP for sources right on the meridian
        """

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

    def TestDeRuiterCalculation(self):
        """Check all the unit conversions are correct"""
        dataset = DataSet(data={'description':"Assoc 1-to-1:" + self._testMethodName})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images, centre_ra=10,
                                                     centre_decl=0)


        #Note ra / ra_fit_err are in degrees.
        # ew_sys_err is in arcseconds, but we set it = 0 so doesn't matter.
        #ra_fit_err cannot be zero or we get div by zero errors.
        #Also, there is a hard limit on association radii:
        #currently this defaults to 0.03 degrees== 108 arcseconds
        src0 = db_subs.example_extractedsource_tuple(ra=10.00, dec=0.0,
                                             error_radius=10.0,
                                             ew_sys_err=0.0, ns_sys_err=0.0)
        src1 = db_subs.example_extractedsource_tuple(ra=10.02, dec=0.0,
                                             error_radius=10.0,
                                             ew_sys_err=0.0, ns_sys_err=0.0)
        src_list = [src0, src1]
        # error on ra used in DR calculation is based on error_radius and sys_err,
        # which are here in arcsec, and thus we have to multiply with 3600.
        # NB dec_fit_err nonzero, but since delta_dec==0 this simplifies to:
        expected_DR_radius = 3600 * math.sqrt((src1.ra - src0.ra) ** 2 /
                               (src0.error_radius ** 2 + src1.error_radius ** 2))

        for idx in [0, 1]:
            image = tkp.db.Image(dataset=dataset,
                                data=im_params[idx])
            image.insert_extracted_sources([src_list[idx]])
            #Peform very loose association since we just want to store DR value.
            associate_extracted_sources(image.id, deRuiter_r=100)
        runcat = columns_from_table('runningcatalog', ['id'],
                                   where={'dataset':dataset.id})
#        print "***\nRESULTS:", runcat, "\n*****"
        self.assertEqual(len(runcat), 1)
        assoc = columns_from_table('assocxtrsource', ['r'],
                                   where={'runcat':runcat[0]['id']})
#        print "Got assocs:", assoc
        self.assertEqual(len(assoc), 2)
        self.assertAlmostEqual(assoc[1]['r'], expected_DR_radius)

    def TestDeRuiterWrapping(self):
        """Check identical DR for source pair rotated over RA"""
        
        dataset = DataSet(data={'description':"Assoc 1-to-1:" + self._testMethodName})
        
        im_list = db_subs.example_dbimage_datasets(n_images=2)
        
        # Base positions for each source pair:
        pos1 = (30.0,10.5)
        pos2 = (pos1[0]+270.0, pos1[1])

        positions = [pos1, pos2]
        sources1 = [db_subs.example_extractedsource_tuple(ra=p[0], dec=p[1])
                    for p in positions]

        image = tkp.db.Image(dataset=dataset, data=im_list[0])
        image.insert_extracted_sources(sources1)
        associate_extracted_sources(image.id, deRuiter_r=3.717)
        
        # Now shift the positions to be associated in both RA and Dec,
        # then make sure we get the same result at both base RA's:
        delta_ra = 50 / 3600.0
        delta_dec = 50 / 3600.0
        positions = [  [pos1[0] + delta_ra, pos1[1] + delta_dec] ,
                      [pos2[0] + delta_ra, pos2[1] + delta_dec]]

        sources2 = [db_subs.example_extractedsource_tuple(ra=p[0], dec=p[1])
                    for p in positions]
        
        expected_dr1 = db_subs.deRuiter_radius(sources1[0], sources2[0])
        expected_dr2 = db_subs.deRuiter_radius(sources1[1], sources2[1])

        image = tkp.db.Image(dataset=dataset, data=im_list[1])
        image.insert_extracted_sources(sources2)
        associate_extracted_sources(image.id, deRuiter_r=1e6)
        
        # Now inspect the contents of assocxtrsource:
        # Order results by runningcatalog id, then DR radius.
        query = """\
        SELECT a.runcat
              ,a.xtrsrc
              ,a.r 
          FROM assocxtrsource a
              ,runningcatalog r 
         WHERE a.runcat = r.id 
           AND r.dataset = %(dataset_id)s
        ORDER BY a.runcat
                ,a.r
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        dr_result = zip(*cursor.fetchall())
        self.assertNotEqual(len(dr_result), 0)
        runcat = dr_result[0]
        xtrsrc = dr_result[1]
        dr_radius = dr_result[2]
        
        self.assertEqual(len(runcat), 4)
        # Ordered by runcat id,so check associations
        # have performed as expected by checking consecutive pairs:
        self.assertEqual(runcat[0], runcat[1])
        self.assertEqual(runcat[2], runcat[3])
        # New sources are assigned DR=0
        self.assertAlmostEqual(dr_radius[0], 0)
        self.assertAlmostEqual(dr_radius[2], 0)
        self.assertAlmostEqual(dr_radius[1], expected_dr1)
        self.assertAlmostEqual(dr_radius[3], expected_dr2)
        

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
                                                     ew_sys_err=20, ns_sys_err=20
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
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.12351, dec=10.551,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
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
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.015, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
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
                                                     ew_sys_err=20, ns_sys_err=20
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


class TestMany2Many(unittest.TestCase):
    """
    These tests will check the many-to-many source associations, 
    i.e. many extractedsources that has two (or more) counterparts in the 
    runningcatalog.
    
    Here we are effectively checking the behaviour of the graph 'pruning' 
    query; _flag_many_to_many_tempruncat(), and also the way those flagged
    associations are then dealt with, e.g. in 
    _insert_1_to_many_basepoint_assoc and _insert_1_to_many_assoc.

    """
    def shortDescription(self):
        return None
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.n_images = 2
        self.src_offset_deg = 20 / 3600.
        self.tiny_offset_deg = 1 / 3600.  # 1 arcsecond
        self.pos_err_deg = 30 / 3600.
        self.dr_limit = 3.717

        self.im_params = db_subs.example_dbimage_datasets(self.n_images,
                                                     centre_ra=123,
                                                     centre_decl=10.5
                                                     )
        # We set a huge beam size as that can limit candidate assocs otherwise.
        self.template_src = db_subs.example_extractedsource_tuple(
                     ra=123, dec=10.5,
                     ra_fit_err=self.pos_err_deg, dec_fit_err=self.pos_err_deg,
                     beam_maj=100, beam_min=100, beam_angle=45,
                     ew_sys_err=0, ns_sys_err=0
                     )

        # 2 'base' sources, East and West of centre.
        # (located relatively close together, allowing for possible
        # multiple associations)
        self.centre_ra = self.template_src.ra
        self.centre_dec = self.template_src.dec
        base_srcs = []
        base_srcs.append(
          self.template_src._replace(ra=self.centre_ra - self.src_offset_deg))
        base_srcs.append(
          self.template_src._replace(ra=self.centre_ra + self.src_offset_deg))
        self.base_srcs = base_srcs

    def tearDown(self):
        """remove all stuff after the test has been run"""
        tkp.db.rollback()
        

    def insert_many_to_many_sources(self, dataset, im_params,
                                    image1_srcs, image2_srcs, dr_limit):
        """
        Load 2 images in the database according to im_params,
        then populate with image1_srcs / image2_srcs accordingly, and
        associate. 
        
        Return dicts representing relevant runcat, and extractedsource
        entries. The 'runcat' dicts have a nested 'assoc' dict added,
        representing their association table entries.
        """
        self.assertEqual(len(im_params), 2)

        # Check that we have chosen sufficiently close sources /
        # suff. large errors / suff. large DR to allow cross-association
        # This ensures that we really are testing the *many to many* case.
        for src_a in image1_srcs:
            for src_b in image2_srcs:
                dr_between_srcs = db_subs.deRuiter_radius(src_a, src_b)
                self.assertTrue(dr_limit > dr_between_srcs)

        image1 = tkp.db.Image(dataset=dataset, data=im_params[0])
        image2 = tkp.db.Image(dataset=dataset, data=im_params[1])
        self.image1 = image1
        self.image2 = image2

        dbgen.insert_extracted_sources(image1.id, image1_srcs, 'blind')
        associate_extracted_sources(image1.id, deRuiter_r=dr_limit)

        dbgen.insert_extracted_sources(image2.id, image2_srcs, 'blind')

#         Double check that we actually get *many-to-many* candidate links:
        assoc_subs._insert_temprunningcatalog(image2.id, dr_limit,
                                    assoc_subs._check_meridian_wrap(image2.id))
        candidate_assocs = columns_from_table('temprunningcatalog')
        self.assertEqual(len(candidate_assocs),
                         len(image1_srcs) * len(image2_srcs))

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

        extracted = columns_from_table('extractedsource',
                                       where={'image':image1.id})
        extracted.extend(columns_from_table('extractedsource',
                                       where={'image':image2.id}))

        # #Use the data we just grabbed to build nested dictionaries,
        # representing the runningcatalog entries and their associated
        #  extractions
        for rc_entry in runcat:
            associated_srcs = []
            for a in associations:
                if a['runcat'] == rc_entry['id']:
                    associated_srcs.append(a)
            rc_entry['assoc'] = associated_srcs

        return runcat, extracted

    @staticmethod
    def summarise_associations(runcat, extracted):
        """Print a nice summary of the results dictionaries
        (as ouput by insert_many_to_many_sources)"""

        print "\nSources input:"
        for ex in sorted(extracted, key=lambda x:x['image']):
            print ', '.join(kw + ':' + str(ex[kw]) for kw in
                             ('image', 'id', 'ra', 'decl'))

        print "\nResulting associations"
        for rc_entry in sorted(runcat, key=lambda x:x['id']):
            print "Runcat:", rc_entry['id']
            print ', '.join(kw + ':' + str(rc_entry[kw]) for kw in
                            ('id', 'wm_ra', 'wm_decl', 'datapoints', 'inactive',
                              'xtrsrc'))
            print "\t Associated extractions:"
            for assoc_entry in sorted(rc_entry['assoc'], key=lambda x:x['image']):
                print '\t', assoc_entry
        print



    def test_many2many_reduced_to_two_1_to_many_one_1to1(self):
        """This handles the case where we have two sources in first image
        and two in second image. 
        The two sources in the second image can be associated with one source
        from the first image, whereas the other source is not assocaited with 
        any from the second image.
        Both sources in the second image can be associated with both sources
        in the first image. However, checking the DR radius reduces the 
        associations to be two of the type 1-to-many and one source in the first
        image that is left unassociated. 
        The runcat will end up with 3 sources.
        All sources are candidate associations with each other (1-3, 1-4, 2-3, 2-4, 
        where '*' is a runcat source and 'o' the lastest extracted sources)

             3
             o
            / \
         1 *   * 2
            \ /
             o
             4

        but only the ones with the smallest DR radius are considered as genuine, leaving

             3
             o
              \
         1 *   * 2
              /
             o
             4

        Here, runcat 1 is left unassociated (to be forced fit later), and extracted sources
        3 and 4 are associated with runcat 2. Because it is a 1-to-many association, runcat
        source 2 is replaced by 3 and 4.
        
        Note that, in this case, assoc-links 3-2, 4-2 have *identical* DR
        radius values, but that's OK - one runcat entry can have multiple 
        associated extractedsources (1-to-many).
        """

        self.picture = r"""
             3
             o
              \
         1 *   * 2
              /
             o
             4
        """

        dataset = DataSet(data={'description': 'assoc test set: n-m, '
                                + self._testMethodName})

#       So in this case, we have 2 sources in image2, offset from centre in
#       Dec, with a slight offset towards positive RA.
        north_src = self.template_src._replace(
                               ra=self.centre_ra + self.tiny_offset_deg,
                               dec=self.centre_dec +self.src_offset_deg,)
        south_src = self.template_src._replace(
                               ra=self.centre_ra + self.tiny_offset_deg,
                               dec=self.centre_dec - self.src_offset_deg,)
        image2_srcs = [north_src, south_src]

        runcat, extracted = self.insert_many_to_many_sources(dataset,
                                         self.im_params,
                                         self.base_srcs, image2_srcs,
                                         dr_limit=3.717)
        # Print summary
#         print
#         print self.picture
#         self.summarise_associations(runcat, extracted)

        # We expect 3 runcat entries: 1 single extraction (at lower RA)
        # and 2 1-to-many associations for the higher RA pairs
        self.assertEqual(len(runcat), 3)

        # Check that the lower RA runcat entry has only one extraction:
        ra_sorted_runcat = sorted(runcat, key=lambda x:x['wm_ra'])
        self.assertEqual(ra_sorted_runcat[0]['datapoints'], 1)
        # And the higher RA both have 2:
        self.assertEqual(ra_sorted_runcat[1]['datapoints'], 2)
        self.assertEqual(ra_sorted_runcat[2]['datapoints'], 2)

        # We can also check the association types:
        single_entry_runcat = ra_sorted_runcat[0]
        self.assertEqual(len(single_entry_runcat['assoc']), 1)  # sanity check
        self.assertEqual(single_entry_runcat['assoc'][0]['type'], 4)
        for rc in ra_sorted_runcat[1:]:
            assocs = rc['assoc']
            self.assertEqual(len(assocs), 2)  # sanity check
            self.assertEqual(assocs[0]['type'], 6)
            self.assertEqual(assocs[1]['type'], 2)


    def test_many2many_reduced_to_two_1to1(self):
        """This handles the case where we have two sources in first image
        and two in second image.
        Both sources in the second image can be associated with both sources
        in the first image. However, checking the DR radius reduces the
        associations to be two of the type 1 to 1.
        The runcat will end up with 2 sources.
        All sources are candidate associations with each other (1-3, 1-4, 2-3, 2-4,
        where '*' is a runcat source and 'o' the lastest extracted sources)

             3
             o
            / \
         1 *   * 2
            \ /
             o
             4

        but we end up with two 1-1 associations, leaving

             3
             o
              \
         1 *   * 2
            \
             o
             4

        """
        dataset = DataSet(data={'description': 'assoc test set: n-m, '
                                + self._testMethodName})
        self.picture = r"""
             3
             o
              \
         1 *   * 2
            \
             o
             4
        """
#       In this case, we have 2 sources in image2, offset from centre in
#       Dec. The north src is also slightly offset towards positive RA,
#       while south -> negative RA.
        north_src = self.template_src._replace(
                               ra=self.centre_ra + self.tiny_offset_deg,
                               dec=self.centre_dec + self.src_offset_deg,)
        south_src = self.template_src._replace(
                               ra=self.centre_ra - self.tiny_offset_deg,
                               dec=self.centre_dec - self.src_offset_deg,)
        image2_srcs = [north_src, south_src]

        runcat, extracted = self.insert_many_to_many_sources(dataset,
                                         self.im_params,
                                         self.base_srcs, image2_srcs,
                                         dr_limit=3.717)
        # Print summary
#         print
#         print self.picture
#         self.summarise_associations(runcat, extracted)

        # We expect 2 runcat entries: both 1-to-1 associations.
        self.assertEqual(len(runcat), 2)

        # Check that both have 2 associated extractions:
        ra_sorted_runcat = sorted(runcat, key=lambda x:x['wm_ra'])
        self.assertEqual(ra_sorted_runcat[0]['datapoints'], 2)
        self.assertEqual(ra_sorted_runcat[1]['datapoints'], 2)

        # Check the association entries:
        for rc in ra_sorted_runcat:
            assocs = rc['assoc']
            self.assertEqual(len(assocs), 2)  # sanity check
            self.assertEqual(assocs[0]['type'], 4)
            self.assertEqual(assocs[1]['type'], 3)

    def test_many2many_pathological_equilateral_rhombus(self):
        """This handles the case where we have two sources in first image and
        two in second image.
        The two sources in the second image are *both equidistant from both
        of the original sources*.

        In this case, it is not clear how to 'prune' the candidate associations,
        and our SQL breaks. The response is to abort with an exception and log
        a sane error. (https://support.astron.nl/lofar_issuetracker/issues/4778)

             3
             o
            / \
         1 *   * 2
            \ /
             o
             4

        """


        dataset = DataSet(data={'description': 'assoc test set: n-m, '
                                + self._testMethodName})

        # So in this case, we have 2 sources in image2, offset from centre in
        # Dec, with *NO* offset in RA.
        north_src = self.template_src._replace(
                               dec=self.centre_dec + self.src_offset_deg,)
        south_src = self.template_src._replace(
                               dec=self.centre_dec - self.src_offset_deg,)
        image2_srcs = [north_src, south_src]

        # We will add a handler to the root logger which catches all log
        # output in a buffer.
        iostream = BytesIO()
        hdlr = logging.StreamHandler(iostream)
        logging.getLogger().addHandler(hdlr)

        # Raises an error, exact type depends on database engine in use:
        with self.assertRaises(tkp.db.Database().RhombusError):
            runcat, extracted = self.insert_many_to_many_sources(dataset,
                                             self.im_params,
                                             self.base_srcs, image2_srcs,
                                             dr_limit=3.717)
        logging.getLogger().removeHandler(hdlr)

        # We want to be sure that the error has been appropriately logged.
        self.assertIn("RhombusError", iostream.getvalue())
