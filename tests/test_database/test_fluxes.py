import unittest2 as unittest
import tkp.db
import tkp.db.general as dbgen
from tkp.db.associations import associate_extracted_sources
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database


class TestOne2OneFlux(unittest.TestCase):
    """
    These tests will check the statistical fluxes of a 1-to-1 source associations
    """
    @requires_database()
    def setUp(self):

        self.database = tkp.db.Database()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        self.database.close()

    def test_one2oneflux(self):
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: 1-1'})
        n_images = 3
        im_params = db_subs.example_dbimage_datasets(n_images)

        src_list = []
        src = db_subs.example_extractedsource_tuple()
        src0 = src._replace(flux=2.0)
        src_list.append(src0)
        src1 = src._replace(flux=2.5)
        src_list.append(src1)
        src2 = src._replace(flux=2.4)
        src_list.append(src2)

        for idx, im in enumerate(im_params):
            image = tkp.db.Image(database=self.database, dataset=dataset, data=im)
            image.insert_extracted_sources([src_list[idx]])
            associate_extracted_sources(image.id, deRuiter_r=3.717)

        query = """\
        SELECT rf.avg_f_int
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        avg_f_int = result[0]
        self.assertEqual(len(avg_f_int), 1)
        self.assertAlmostEqual(avg_f_int[0], 2.3)

        # Check evolution of variability indices
        query = """\
        select a.runcat
              ,a.xtrsrc
              ,a.v_int
              ,a.eta_int
          from assocxtrsource a
              ,extractedsource x
              ,image i
         where a.xtrsrc = x.id
           and x.image = i.id
           and i.dataset = %(dataset)s
        order by i.taustart_ts
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        runcat = result[0]
        xtrsrc = result[1]
        v_int = result[2]
        eta_int = result[3]
        self.assertEqual(len(runcat), n_images)
        v_nu = (0,0.15713484026367724,0.11503266569845851)
        eta_nu = (0,500000,280000)
        for i in range(len(runcat)):
            self.assertAlmostEqual(v_int[i], v_nu[i])
            self.assertAlmostEqual(eta_int[i], eta_nu[i])

class TestOne2ManyFlux(unittest.TestCase):
    """
    These tests will check the 1-to-many source associations, i.e. two extractedsources
    have the same one counterpart in the runningcatalog
    """
    @requires_database()
    def setUp(self):

        self.database = tkp.db.Database()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        self.database.close()

    def test_one2manyflux(self):
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: 1-n'})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid1 = image.id
        src = []
        # 1 source
        src.append(db_subs.example_extractedsource_tuple(ra=123.1235, dec=10.55,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.5, peak_err = 5e-1,
                                                     flux = 3.0, flux_err = 5e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src[-1])
        dbgen.insert_extracted_sources(imageid1, results, 'blind')
        associate_extracted_sources(imageid1, deRuiter_r=3.717)

        # image 2
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid2 = image.id
        src = []
        # 2 sources (located close to source 1, catching the 1-to-many case
        src.append(db_subs.example_extractedsource_tuple(ra=123.12349, dec=10.549,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.6, peak_err = 5e-1,
                                                     flux = 3.2, flux_err = 5e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.12351, dec=10.551,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.9, peak_err = 5e-1,
                                                     flux = 3.4, flux_err = 5e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src[0])
        results.append(src[1])
        dbgen.insert_extracted_sources(imageid2, results, 'blind')
        associate_extracted_sources(imageid2, deRuiter_r=3.717)

        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int/avg_f_int_weight as wI
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY rf.avg_f_int
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        avg_f_int = result[0]
        avg_f_int_sq = result[1]
        wI = result[2]
        self.assertEqual(len(avg_f_int), 2)
        self.assertAlmostEqual(avg_f_int[0], 3.1)
        self.assertAlmostEqual(avg_f_int[1], 3.2)
        self.assertAlmostEqual(avg_f_int_sq[0], 9.62)
        self.assertAlmostEqual(avg_f_int_sq[1], 10.28)
        self.assertAlmostEqual(wI[0], 3.1)
        self.assertAlmostEqual(wI[1], 3.2)

        # Check evolution of variability indices
        query = """\
        select a.runcat
              ,a.xtrsrc
              ,a.v_int
              ,a.eta_int
          from assocxtrsource a
              ,runningcatalog r
         where a.runcat = r.id
           and r.dataset = %(dataset)s
        order by a.runcat
                ,a.xtrsrc
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        runcat = result[0]
        xtrsrc = result[1]
        v_int = result[2]
        eta_int = result[3]
        self.assertEqual(len(runcat), 4)
        v_nu = (0, 0.088388347648315532, 0, 0.045619792334615487)
        eta_nu = (0, 0.32, 0, 0.08)
        for i in range(len(runcat)):
            self.assertAlmostEqual(v_int[i], v_nu[i])
            self.assertAlmostEqual(eta_int[i], eta_nu[i])

class TestMany2OneFlux(unittest.TestCase):
    """
    These tests will check the many-to-1 source associations, i.e. one extractedsource
    that has two (or more) counterparts in the runningcatalog.

    """
    @requires_database()
    def setUp(self):

        self.database = tkp.db.Database()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        self.database.close()

    def test_many2oneflux(self):
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: n-1'})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid1 = image.id
        src = []
        # 2 sources (located close together, so the catching the many-to-1 case in next image
        src.append(db_subs.example_extractedsource_tuple(ra=122.985, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.6, peak_err = 5e-1,
                                                     flux = 3.2, flux_err = 5e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src.append(db_subs.example_extractedsource_tuple(ra=123.015, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.9, peak_err = 5e-1,
                                                     flux = 3.4, flux_err = 5e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src[0])
        results.append(src[1])
        dbgen.insert_extracted_sources(imageid1, results, 'blind')
        associate_extracted_sources(imageid1, deRuiter_r = 3.717)

        # image 2
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid2 = image.id
        src = []
        # 1 source
        src.append(db_subs.example_extractedsource_tuple(ra=123.0, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.5, peak_err = 5e-1,
                                                     flux = 3.0, flux_err = 5e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src[-1])
        dbgen.insert_extracted_sources(imageid2, results, 'blind')
        associate_extracted_sources(imageid2, deRuiter_r = 3.717)

        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int/avg_f_int_weight as wI
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY rf.avg_f_int
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        avg_f_int = result[0]
        avg_f_int_sq = result[1]
        wI = result[2]
        self.assertEqual(len(avg_f_int), 2)
        self.assertAlmostEqual(avg_f_int[0], 3.1)
        self.assertAlmostEqual(avg_f_int[1], 3.2)
        self.assertAlmostEqual(avg_f_int_sq[0], 9.62)
        self.assertAlmostEqual(avg_f_int_sq[1], 10.28)
        self.assertAlmostEqual(wI[0], 3.1)
        self.assertAlmostEqual(wI[1], 3.2)

        # Check evolution of variability indices
        query = """\
        select a.runcat
              ,a.xtrsrc
              ,a.v_int
              ,a.eta_int
          from assocxtrsource a
              ,runningcatalog r
         where a.runcat = r.id
           and r.dataset = %(dataset)s
        order by a.runcat
                ,a.xtrsrc
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        runcat = result[0]
        xtrsrc = result[1]
        v_int = result[2]
        eta_int = result[3]
        self.assertEqual(len(runcat), 4)
        v_nu = (0, 0.045619792334615487, 0, 0.088388347648315532)
        eta_nu = (0, 0.08, 0, 0.32)
        for i in range(len(runcat)):
            self.assertAlmostEqual(v_int[i], v_nu[i])
            self.assertAlmostEqual(eta_int[i], eta_nu[i])


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
        self.database.close()

    def test_many2manyflux_reduced_to_two_1_to_many_one_1to1(self):
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: n-m, ' + self._testMethodName})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid1 = image.id
        src1 = []
        # 2 sources (located relatively close together, so the catching the many-to-1 case in next image
        src1.append(db_subs.example_extractedsource_tuple(ra=122.983, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.5, peak_err = 1e-1,
                                                     flux = 3.0, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src1.append(db_subs.example_extractedsource_tuple(ra=123.017, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.7, peak_err = 1e-1,
                                                     flux = 3.2, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src1[0])
        results.append(src1[1])
        dbgen.insert_extracted_sources(imageid1, results, 'blind')
        # We use a default value of 3.717
        associate_extracted_sources(imageid1, deRuiter_r = 3.717)

        # image 2
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid2 = image.id
        src2 = []
        # 2 sources, where both can be associated with both from image 1
        src2.append(db_subs.example_extractedsource_tuple(ra=123.0001, dec=10.483,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.8, peak_err = 1e-1,
                                                     flux = 3.3, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src2.append(db_subs.example_extractedsource_tuple(ra=123.0001, dec=10.518,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.4, peak_err = 1e-1,
                                                     flux = 2.9, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src2[0])
        results.append(src2[1])
        dbgen.insert_extracted_sources(imageid2, results, 'blind')
        associate_extracted_sources(imageid2, deRuiter_r = 3.717)

        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int/avg_f_int_weight as wI
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY rf.avg_f_int
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        avg_f_int = result[0]
        avg_f_int_sq = result[1]
        wI = result[2]
        self.assertEqual(len(avg_f_int), 3)
        self.assertAlmostEqual(avg_f_int[0], 3.0)
        self.assertAlmostEqual(avg_f_int[1], 3.05)
        self.assertAlmostEqual(avg_f_int[2], 3.25)
        self.assertAlmostEqual(avg_f_int_sq[0], 9.0)
        self.assertAlmostEqual(avg_f_int_sq[1], 9.325)
        self.assertAlmostEqual(avg_f_int_sq[2], 10.565)
        self.assertAlmostEqual(wI[0], 3.0)
        self.assertAlmostEqual(wI[1], 3.05)
        self.assertAlmostEqual(wI[2], 3.25)

        # Check evolution of variability indices
        query = """\
        select a.runcat
              ,a.xtrsrc
              ,a.v_int
              ,a.eta_int
          from assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
              ,image i
         where a.runcat = r.id
           and a.xtrsrc = x.id
           and x.image = i.id
           and r.dataset = %(dataset)s
        order by runcat
                ,taustart_ts
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        runcat = result[0]
        xtrsrc = result[1]
        v_int = result[2]
        eta_int = result[3]
        self.assertEqual(len(runcat), 5)
        v_nu = (0, 0, 0.06955148667409071, 0, 0.021757131728822411)
        eta_nu = (0, 0, 4.5, 0, 0.5)
        for i in range(len(runcat)):
            self.assertAlmostEqual(v_int[i], v_nu[i])
            self.assertAlmostEqual(eta_int[i], eta_nu[i])

    def test_many2manyflux_reduced_to_two_1to1(self):
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: n-m, ' + self._testMethodName})
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        # image 1
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid1 = image.id
        src1 = []
        # 2 sources (located relatively close together, so the catching the many-to-1 case in next image
        src1.append(db_subs.example_extractedsource_tuple(ra=122.983, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.5, peak_err = 1e-1,
                                                     flux = 3.0, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src1.append(db_subs.example_extractedsource_tuple(ra=123.017, dec=10.5,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.7, peak_err = 1e-1,
                                                     flux = 3.2, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src1[0])
        results.append(src1[1])
        dbgen.insert_extracted_sources(imageid1, results, 'blind')
        # We use a default value of 3.717
        associate_extracted_sources(imageid1, deRuiter_r = 3.717)

        # image 2
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid2 = image.id
        src2 = []
        # 2 sources, where both can be associated with both from image 1
        src2.append(db_subs.example_extractedsource_tuple(ra=123.005, dec=10.483,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.8, peak_err = 1e-1,
                                                     flux = 3.3, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        src2.append(db_subs.example_extractedsource_tuple(ra=122.99, dec=10.51,
                                                     ra_fit_err=5./3600, dec_fit_err=6./3600,
                                                     peak = 1.4, peak_err = 1e-1,
                                                     flux = 2.9, flux_err = 1e-1,
                                                     sigma = 15,
                                                     beam_maj = 100, beam_min = 100, beam_angle = 45,
                                                     ew_sys_err=20, ns_sys_err=20
                                                        ))
        results = []
        results.append(src2[0])
        results.append(src2[1])
        dbgen.insert_extracted_sources(imageid2, results, 'blind')
        associate_extracted_sources(imageid2, deRuiter_r = 3.717)

        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int/avg_f_int_weight as wI
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY rf.avg_f_int
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        avg_f_int = result[0]
        avg_f_int_sq = result[1]
        wI = result[2]
        self.assertEqual(len(avg_f_int), 2)
        self.assertAlmostEqual(avg_f_int[0], 2.95)
        self.assertAlmostEqual(avg_f_int[1], 3.25)
        self.assertAlmostEqual(avg_f_int_sq[0], 8.705)
        self.assertAlmostEqual(avg_f_int_sq[1], 10.565)
        self.assertAlmostEqual(wI[0], 2.95)
        self.assertAlmostEqual(wI[1], 3.25)

        # Check evolution of variability indices
        query = """\
        select a.runcat
              ,a.xtrsrc
              ,a.v_int
              ,a.eta_int
          from assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
              ,image i
         where a.runcat = r.id
           and a.xtrsrc = x.id
           and x.image = i.id
           and r.dataset = %(dataset)s
        order by runcat
                ,taustart_ts
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        result = zip(*self.database.cursor.fetchall())
        runcat = result[0]
        xtrsrc = result[1]
        v_int = result[2]
        eta_int = result[3]
        self.assertEqual(len(runcat), 4)
        v_nu = (0, 0.023969721396151767, 0, 0.021757131728822411)
        eta_nu = (0, 0.5, 0, 0.5)
        for i in range(len(runcat)):
            self.assertAlmostEqual(v_int[i], v_nu[i])
            self.assertAlmostEqual(eta_int[i], eta_nu[i])


