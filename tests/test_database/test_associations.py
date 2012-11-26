import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import math
import tkp.database as tkpdb
import tkp.database.utils.general as dbgen
import tests.db_subs as db_subs
from tkp.testutil.decorators import requires_database


class TestOne2One(unittest.TestCase):
    """
    These tests will check the 1-to-1 source associations, i.e. an extractedsource
    has exactly one counterpart in the runningcatalog
    """
    @requires_database()
    def setUp(self):

        self.database = tkpdb.DataBase()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        #self.database.connection.rollback()
        #self.database.execute("delete from assocxtrsource")
        #self.database.execute("delete from runningcatalog_flux")
        #self.database.execute("delete from runningcatalog")
        self.database.close()

    def test_one2one(self):
        dataset = tkpdb.DataSet(database=self.database, data={'description': 'assoc test set: 1-1'})
        n_images = 8
        im_params = db_subs.example_dbimage_datasets(n_images)

        steady_srcs = []
        n_steady_srcs = 3
        for i in range(n_steady_srcs):
            src = db_subs.example_extractedsource_tuple()
            src = src._replace(ra=src.ra + 2 * i)
            steady_srcs.append(src)

        for im in im_params:
            image = tkpdb.Image(database=self.database, dataset=dataset, data=im)
            image.insert_extracted_sources(steady_srcs)
            image.associate_extracted_sources()

        # Check runningcatalog, runningcatalog_flux, assocxtrsource
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
        """
        self.database.cursor.execute(query, (dataset.id,))
        runcat = zip(*self.database.cursor.fetchall())
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
                           1./ (n_images / ((steady_srcs[0].ra_err*3600.)**2)) 
                               ))
        self.assertAlmostEqual(wm_decl_err[0], math.sqrt( 
                           1./ (n_images / ((steady_srcs[0].dec_err*3600.)**2)) 
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
        self.database.cursor.execute(query, (dataset.id,))
        assoc = zip(*self.database.cursor.fetchall())
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
        self.database.cursor.execute(query, (dataset.id,))
        xtrsrcs = zip(*self.database.cursor.fetchall())
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
        self.database.cursor.execute(query, (dataset.id,))
        fluxes = zip(*self.database.cursor.fetchall())
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

class TestOne2Many(unittest.TestCase):
    """
    These tests will check the 1-to-many source associations, i.e. two extractedsources
    have the same one counterpart in the runningcatalog
    """
    @requires_database()
    def setUp(self):

        self.database = tkpdb.DataBase()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        #self.database.connection.rollback()
        #self.database.execute("delete from assocxtrsource")
        #self.database.execute("delete from runningcatalog_flux")
        #self.database.execute("delete from runningcatalog")
        self.database.close()

    def test_one2many(self):
        dataset = tkpdb.DataSet(database=self.database, data={'description': 'assoc test set: 1-n'})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkpdb.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid1 = image.id
        src = []
        # 1 source
        src.append(db_subs.example_extractedsource_tuple(ra=123.1235, dec=10.55,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        results = []
        results.append(src[-1])
        dbgen.insert_extracted_sources(self.database.connection, image.id, results)
        tkpdb.utils.associate_extracted_sources(self.database.connection, image.id)
        
        query = """\
        SELECT id
          FROM extractedsource 
         WHERE image = %s
        """
        self.database.cursor.execute(query, (image.id,))
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
        image = tkpdb.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid2 = image.id
        src = []
        # 2 sources (located close to source 1, catching the 1-to-many case
        src.append(db_subs.example_extractedsource_tuple(ra=123.12349, dec=10.549,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.12351, dec=10.551,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        results = []
        results.append(src[0])
        results.append(src[1])
        dbgen.insert_extracted_sources(self.database.connection, image.id, results)
        tkpdb.utils.associate_extracted_sources(self.database.connection, image.id)

        query = """\
        SELECT id
          FROM extractedsource 
         WHERE image = %s
        ORDER BY id
        """
        self.database.cursor.execute(query, (image.id,))
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

        self.database = tkpdb.DataBase()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        #self.database.connection.rollback()
        #self.database.execute("delete from assocxtrsource")
        #self.database.execute("delete from runningcatalog_flux")
        #self.database.execute("delete from runningcatalog")
        self.database.close()

    def test_many2one(self):
        dataset = tkpdb.DataSet(database=self.database, data={'description': 'assoc test set: n-1'})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkpdb.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid1 = image.id
        src = []
        # 2 sources (located close together, so the catching the many-to-1 case in next image
        src.append(db_subs.example_extractedsource_tuple(ra=123.12349, dec=10.549,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.12351, dec=10.551,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        results = []
        results.append(src[0])
        results.append(src[1])
        dbgen.insert_extracted_sources(self.database.connection, imageid1, results)
        tkpdb.utils.associate_extracted_sources(self.database.connection, imageid1)

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
        image = tkpdb.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid2 = image.id
        src = []
        # 1 source
        src.append(db_subs.example_extractedsource_tuple(ra=123.1235, dec=10.55,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        results = []
        results.append(src[-1])
        dbgen.insert_extracted_sources(self.database.connection, imageid2, results)
        tkpdb.utils.associate_extracted_sources(self.database.connection, imageid2)
        
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
              ,a.xtrsrc
              ,a.type
              ,x.image 
          FROM assocxtrsource a
              ,runningcatalog r
              ,extractedsource x 
         WHERE a.runcat = r.id 
           AND a.xtrsrc = x.id 
           AND r.dataset = %s 
        ORDER BY xtrsrc
                ,runcat
        """
        self.database.cursor.execute(query, (dataset.id,))
        assoc2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(assoc2), 0)
        aruncat2 = assoc2[0]
        axtrsrc2 = assoc2[1]
        atype2 = assoc2[2]
        aimage2 = assoc2[3]
        self.assertEqual(len(aruncat2), 4)
        self.assertEqual(aruncat2[0], aruncat2[2])
        self.assertEqual(aruncat2[1], aruncat2[3])
        self.assertEqual(axtrsrc2[0], im1src[0])
        self.assertEqual(axtrsrc2[1], im1src[1])
        self.assertEqual(axtrsrc2[2], im2src[0])
        self.assertEqual(axtrsrc2[3], im2src[0])
        self.assertEqual(atype2[0], 4)
        self.assertEqual(atype2[1], 4)
        self.assertEqual(atype2[2], 3)
        self.assertEqual(atype2[3], 3)
        self.assertEqual(aimage2[0], imageid1)
        self.assertEqual(aimage2[1], imageid1)
        self.assertEqual(aimage2[2], imageid2)
        self.assertEqual(aimage2[3], imageid2)
        #TODO: Add runcat_flux test

class TestMany2Many(unittest.TestCase):
    """
    These tests will check the many-to-many source associations, i.e. many extractedsources
    that has two (or more) counterparts in the runningcatalog.

    """
    @requires_database()
    def setUp(self):

        self.database = tkpdb.DataBase()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        #self.database.connection.rollback()
        #self.database.execute("delete from assocxtrsource")
        #self.database.execute("delete from runningcatalog_flux")
        #self.database.execute("delete from runningcatalog")
        self.database.close()

    def test_many2many(self):
        dataset = tkpdb.DataSet(database=self.database, data={'description': 'assoc test set: n-m'})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkpdb.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid1 = image.id
        src1 = []
        # 2 sources (located close together, so the catching the many-to-1 case in next image
        src1.append(db_subs.example_extractedsource_tuple(ra=123.12349, dec=10.549,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        src1.append(db_subs.example_extractedsource_tuple(ra=123.12351, dec=10.551,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        results = []
        results.append(src1[0])
        results.append(src1[1])
        dbgen.insert_extracted_sources(self.database.connection, imageid1, results)
        tkpdb.utils.associate_extracted_sources(self.database.connection, imageid1)

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
        self.assertEqual(len(im1src), len(src1))
        
        # image 2
        image = tkpdb.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid2 = image.id
        src2 = []
        # 2 sources as well
        src2.append(db_subs.example_extractedsource_tuple(ra=123.12348, dec=10.548,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        src2.append(db_subs.example_extractedsource_tuple(ra=123.12352, dec=10.552,
                                                     ra_err=5./3600, dec_err=6./3600, 
                                                     peak = 15e-3, peak_err = 5e-4,
                                                     flux = 15e-3, flux_err = 5e-4,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45
                                                        ))
        results = []
        results.append(src2[0])
        results.append(src2[1])
        dbgen.insert_extracted_sources(self.database.connection, imageid2, results)
        tkpdb.utils.associate_extracted_sources(self.database.connection, imageid2)
        
        query = """\
        SELECT id
          FROM extractedsource 
         WHERE image = %s
        """
        self.database.cursor.execute(query, (imageid2,))
        im2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(im2), 0)
        im2src = im2[0]
        self.assertEqual(len(im2src), len(src2))

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
              ,a.xtrsrc
              ,a.type
              ,x.image 
          FROM assocxtrsource a
              ,runningcatalog r
              ,extractedsource x 
         WHERE a.runcat = r.id 
           AND a.xtrsrc = x.id 
           AND r.dataset = %s
        ORDER BY xtrsrc
                ,runcat
        """
        self.database.cursor.execute(query, (dataset.id,))
        assoc2 = zip(*self.database.cursor.fetchall())
        self.assertNotEqual(len(assoc2), 0)
        aruncat2 = assoc2[0]
        axtrsrc2 = assoc2[1]
        atype2 = assoc2[2]
        aimage2 = assoc2[3]
        self.assertEqual(len(aruncat2), 4)
        self.assertEqual(aruncat2[0], aruncat2[2])
        self.assertEqual(aruncat2[1], aruncat2[3])
        self.assertEqual(axtrsrc2[0], im1src[0])
        self.assertEqual(axtrsrc2[1], im1src[1])
        self.assertEqual(axtrsrc2[2], im2src[0])
        self.assertEqual(axtrsrc2[3], im2src[1])
        self.assertEqual(atype2[0], 4)
        self.assertEqual(atype2[1], 4)
        self.assertEqual(atype2[2], 3)
        self.assertEqual(atype2[3], 3)
        self.assertEqual(aimage2[0], imageid1)
        self.assertEqual(aimage2[1], imageid1)
        self.assertEqual(aimage2[2], imageid2)
        self.assertEqual(aimage2[3], imageid2)
        #TODO: Add runcat_flux test

