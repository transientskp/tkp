import unittest
import tkp.db
import tkp.db.general as dbgen
from tkp.db.generic import  get_db_rows_as_dicts, columns_from_table
from tkp.db.associations import associate_extracted_sources
from tkp.testutil import db_subs
from tkp.testutil import db_queries
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
        im_params = db_subs.generate_timespaced_dbimages_data(n_images)

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
        py_metrics = db_subs.lightcurve_metrics(src_list)
        self.assertAlmostEqual(avg_f_int[0], py_metrics[-1]['avg_f_int'])
        runcat_id = columns_from_table('runningcatalog',
                                       where={'dataset':dataset.id})
        self.assertEqual(len(runcat_id),1)
        runcat_id = runcat_id[0]['id']
        # Check evolution of variability indices
        db_metrics = db_queries.get_assoc_entries(self.database,
                                                           runcat_id)
        self.assertEqual(len(db_metrics), n_images)
        # Compare the python- and db-calculated values
        for i in range(len(db_metrics)):
            for key in ('v_int','eta_int'):
                self.assertAlmostEqual(db_metrics[i][key], py_metrics[i][key])


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
        dataset = tkp.db.DataSet(database=self.database,
                                 data={'description': 'flux test set: 1-n'})
        n_images = 2
        im_params = db_subs.generate_timespaced_dbimages_data(n_images)
        central_ra, central_dec = 123.1235, 10.55,
        position_offset_deg = 100./3600 #100 arcsec = 0.03 deg approx

        # image 1
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[0])
        imageid1 = image.id

        img1_srclist = []
        # 1 source
        img1_srclist.append(db_subs.example_extractedsource_tuple(central_ra, central_dec,
                                         peak = 1.5, peak_err = 5e-1,
                                         flux = 3.0, flux_err = 5e-1,
                                            ))

        dbgen.insert_extracted_sources(imageid1, img1_srclist, 'blind')
        associate_extracted_sources(imageid1, deRuiter_r=3.717)

        # image 2
        image = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[1])
        imageid2 = image.id
        img2_srclist = []
        # 2 sources (both close to source 1, catching the 1-to-many case)
        img2_srclist.append(db_subs.example_extractedsource_tuple(
            central_ra,
            central_dec,
            peak = 1.6, peak_err = 5e-1,
            flux = 3.2, flux_err = 5e-1,
            ))
        img2_srclist.append(db_subs.example_extractedsource_tuple(
            central_ra + position_offset_deg,
            central_dec,
            peak = 1.9, peak_err = 5e-1,
            flux = 3.4, flux_err = 5e-1,
            ))

        dbgen.insert_extracted_sources(imageid2, img2_srclist, 'blind')
        associate_extracted_sources(imageid2, deRuiter_r=3.717)

        # Manually compose the lists of sources we expect to see associated
        # into runningcatalog entries:
        # NB img2_srclist[1] has larger RA value.
        lightcurves_sorted_by_ra =[]
        lightcurves_sorted_by_ra.append( [img1_srclist[0], img2_srclist[0]])
        lightcurves_sorted_by_ra.append( [img1_srclist[0], img2_srclist[1]])


        #Check the summary statistics (avg flux, etc)
        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int
              ,avg_f_int_weight
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY r.wm_ra
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        runcat_flux_entries = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(runcat_flux_entries), 2)
        for idx, flux_summary in enumerate(runcat_flux_entries):
            py_results = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            for key in flux_summary.keys():
                self.assertAlmostEqual(flux_summary[key], py_results[-1][key])


        #Now check the per-timestep statistics (variability indices)
        sorted_runcat_ids = columns_from_table('runningcatalog',
                                               where={'dataset':dataset.id},
                                               order='wm_ra')
        sorted_runcat_ids = [entry['id'] for entry in sorted_runcat_ids]

        for idx, rcid in enumerate(sorted_runcat_ids):
            db_indices = db_queries.get_assoc_entries(self.database,
                                                                   rcid)
            py_indices = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            self.assertEqual(len(db_indices), len(py_indices))
            for nstep in range(len(db_indices)):
                for key in ('v_int', 'eta_int', 'f_datapoints'):
                    self.assertAlmostEqual(db_indices[nstep][key],
                                           py_indices[nstep][key])


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
        central_ra, central_dec = 123.1235, 10.55,
        position_offset_deg = 100./3600 #100 arcsec = 0.03 deg approx

        im_params = db_subs.generate_timespaced_dbimages_data(n_images)
        # image 1
        image1 = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[0])
        img1_srclist = []
        # 2 sources (located close together, so the catching the many-to-1 case in next image

        img1_srclist.append(db_subs.example_extractedsource_tuple(
            ra=central_ra,
            dec=central_dec,
            peak = 1.6, peak_err = 5e-1,
            flux = 3.2, flux_err = 5e-1,
            ))
        img1_srclist.append(db_subs.example_extractedsource_tuple(
            ra=central_ra + position_offset_deg,
            dec=central_dec,
            peak = 1.9, peak_err = 5e-1,
            flux = 3.4, flux_err = 5e-1,
            ))

        dbgen.insert_extracted_sources(image1.id, img1_srclist, 'blind')
        associate_extracted_sources(image1.id, deRuiter_r=3.717)

        # image 2
        image2 = tkp.db.Image(database=self.database, dataset=dataset, data=im_params[1])
        img2_srclist = []
        # 1 source
        img2_srclist.append(db_subs.example_extractedsource_tuple(
            ra=central_ra,
            dec=central_dec,
            peak = 1.5, peak_err = 5e-1,
            flux = 3.0, flux_err = 5e-1,
            ))

        dbgen.insert_extracted_sources(image2.id, img2_srclist, 'blind')
        associate_extracted_sources(image2.id, deRuiter_r=3.717)

        # Manually compose the lists of sources we expect to see associated
        # into runningcatalog entries:
        # NB img1_srclist[1] has larger RA value.
        lightcurves_sorted_by_ra =[]
        lightcurves_sorted_by_ra.append( [img1_srclist[0], img2_srclist[0]])
        lightcurves_sorted_by_ra.append( [img1_srclist[1], img2_srclist[0]])

        #Check the summary statistics (avg flux, etc)
        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int
              ,avg_f_int_weight
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY r.wm_ra
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        runcat_flux_entries = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(runcat_flux_entries), 2)

        for idx, flux_summary in enumerate(runcat_flux_entries):
            py_results = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            for key in flux_summary.keys():
                self.assertAlmostEqual(flux_summary[key], py_results[-1][key])


        #Now check the per-timestep statistics (variability indices)
        sorted_runcat_ids = columns_from_table('runningcatalog',
                                               where={'dataset':dataset.id},
                                               order='wm_ra')
        sorted_runcat_ids = [entry['id'] for entry in sorted_runcat_ids]

        for idx, rcid in enumerate(sorted_runcat_ids):
            db_indices = db_queries.get_assoc_entries(self.database,
                                                                   rcid)
            py_indices = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            self.assertEqual(len(db_indices), len(py_indices))
            for nstep in range(len(db_indices)):
                for key in ('v_int', 'eta_int', 'f_datapoints'):
                    self.assertAlmostEqual(db_indices[nstep][key],
                                           py_indices[nstep][key])


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
        """
        (See also assoc. test test_many2many_reduced_to_two_1_to_many_one_1to1 )
        In this test-case we cross-associate between a rhombus of sources spread
        about a central position, east-west in the first image,
        north-south in the second.

        The latter, north-south pair are both slightly offset towards positive RA.

        The result is that they are both linked with the high-RA (eastern) source
        in one-to-many associations.
        """
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: n-m, ' + self._testMethodName})
        n_images = 2
        im_params = db_subs.generate_timespaced_dbimages_data(n_images)
        centre_ra, centre_dec =  123., 10.5,
        offset_deg = 20 / 3600. #20 arcsec
        tiny_offset_deg = 1 / 3600. #1 arcsec

        eastern_src = db_subs.example_extractedsource_tuple(
            ra=centre_ra + offset_deg,
            dec=centre_dec,
            peak = 1.5, peak_err = 1e-1,
            flux = 3.0, flux_err = 1e-1,)

        western_src = db_subs.example_extractedsource_tuple(
            ra=centre_ra - offset_deg,
            dec=centre_dec,
            peak = 1.7, peak_err = 1e-1,
            flux = 3.2, flux_err = 1e-1,)

        northern_source = db_subs.example_extractedsource_tuple(
            ra=centre_ra + tiny_offset_deg,
            dec=centre_dec + offset_deg,
            peak = 1.8, peak_err = 1e-1,
            flux = 3.3, flux_err = 1e-1,
            )

        southern_source = db_subs.example_extractedsource_tuple(
            ra=centre_ra + tiny_offset_deg,
            dec=centre_dec - offset_deg,
            peak = 1.4, peak_err = 1e-1,
            flux = 2.9, flux_err = 1e-1,)

        # image 1
        image1 = tkp.db.Image(database=self.database, dataset=dataset,
                              data=im_params[0])
        dbgen.insert_extracted_sources(
            image1.id, [eastern_src,western_src], 'blind')
        associate_extracted_sources(image1.id, deRuiter_r=3.717)

        # image 2
        image2 = tkp.db.Image(database=self.database, dataset=dataset,
                              data=im_params[1])
        dbgen.insert_extracted_sources(
            image2.id, [northern_source, southern_source], 'blind')
        associate_extracted_sources(image2.id, deRuiter_r=3.717)

        # Manually compose the lists of sources we expect to see associated
        # into runningcatalog entries:
        # NB img1_srclist[1] has larger RA value.
        lightcurves_sorted_by_ra_dec =[]
        lightcurves_sorted_by_ra_dec.append( [western_src])
        lightcurves_sorted_by_ra_dec.append( [eastern_src, southern_source])
        lightcurves_sorted_by_ra_dec.append( [eastern_src, northern_source])

        #Check the summary statistics (avg flux, etc)
        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int
              ,avg_f_int_weight
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY r.wm_ra, r.wm_decl
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        runcat_flux_entries = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(runcat_flux_entries), len(lightcurves_sorted_by_ra_dec))

        for idx, flux_summary in enumerate(runcat_flux_entries):
            py_results = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra_dec[idx])
            for key in flux_summary.keys():
                self.assertAlmostEqual(flux_summary[key], py_results[-1][key])

        #Now check the per-timestep statistics (variability indices)
        sorted_runcat_ids = columns_from_table('runningcatalog',
                                               where={'dataset':dataset.id},
                                               order='wm_ra,wm_decl')
        sorted_runcat_ids = [entry['id'] for entry in sorted_runcat_ids]

        for idx, rcid in enumerate(sorted_runcat_ids):
            db_indices = db_queries.get_assoc_entries(self.database,
                                                                   rcid)
            py_indices = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra_dec[idx])
            self.assertEqual(len(db_indices), len(py_indices))
            for nstep in range(len(db_indices)):
                for key in ('v_int', 'eta_int', 'f_datapoints'):
                    self.assertAlmostEqual(db_indices[nstep][key],
                                           py_indices[nstep][key])

    def test_many2manyflux_reduced_to_two_1to1(self):
        """
        (See also assoc. test test_many2many_reduced_to_two_1to1 )
        In this test-case we cross-associate between a rhombus of sources spread
        about a central position, east-west in the first image,
        north-south in the second.

        The latter, north-south pair are slightly offset towards positive RA
        and negative RA respectively.

        The result is that the candidate associations are pruned down to
        two one-to-one pairings..
        """
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: n-m, ' + self._testMethodName})
        n_images = 2
        im_params = db_subs.generate_timespaced_dbimages_data(n_images)
        centre_ra, centre_dec =  123., 10.5,
        offset_deg = 20 / 3600. #20 arcsec
        tiny_offset_deg = 1 / 3600. #1 arcsec

        eastern_src = db_subs.example_extractedsource_tuple(
            ra=centre_ra + offset_deg,
            dec=centre_dec,
            peak = 1.5, peak_err = 1e-1,
            flux = 3.0, flux_err = 1e-1,)

        western_src = db_subs.example_extractedsource_tuple(
            ra=centre_ra - offset_deg,
            dec=centre_dec,
            peak = 1.7, peak_err = 1e-1,
            flux = 3.2, flux_err = 1e-1,)

        northern_source = db_subs.example_extractedsource_tuple(
            ra=centre_ra + tiny_offset_deg,
            dec=centre_dec + offset_deg,
            peak = 1.8, peak_err = 1e-1,
            flux = 3.3, flux_err = 1e-1,
            )

        southern_source = db_subs.example_extractedsource_tuple(
            ra=centre_ra - tiny_offset_deg,
            dec=centre_dec - offset_deg,
            peak = 1.4, peak_err = 1e-1,
            flux = 2.9, flux_err = 1e-1,)

        # image 1
        image1 = tkp.db.Image(database=self.database, dataset=dataset,
                              data=im_params[0])
        dbgen.insert_extracted_sources(
            image1.id, [eastern_src,western_src], 'blind')
        associate_extracted_sources(image1.id, deRuiter_r=3.717)

        # image 2
        image2 = tkp.db.Image(database=self.database, dataset=dataset,
                              data=im_params[1])
        dbgen.insert_extracted_sources(
            image2.id, [northern_source, southern_source], 'blind')
        associate_extracted_sources(image2.id, deRuiter_r=3.717)

        # Manually compose the lists of sources we expect to see associated
        # into runningcatalog entries:
        # NB img1_srclist[1] has larger RA value.
        lightcurves_sorted_by_ra =[]
        lightcurves_sorted_by_ra.append( [western_src, southern_source])
        lightcurves_sorted_by_ra.append( [eastern_src, northern_source])

        #Check the summary statistics (avg flux, etc)
        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int
              ,avg_f_int_weight
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY r.wm_ra, r.wm_decl
        """
        self.database.cursor.execute(query, {'dataset': dataset.id})
        runcat_flux_entries = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(runcat_flux_entries), len(lightcurves_sorted_by_ra))

        for idx, flux_summary in enumerate(runcat_flux_entries):
            py_results = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            for key in flux_summary.keys():
                self.assertAlmostEqual(flux_summary[key], py_results[-1][key])

        #Now check the per-timestep statistics (variability indices)
        sorted_runcat_ids = columns_from_table('runningcatalog',
                                               where={'dataset':dataset.id},
                                               order='wm_ra,wm_decl')
        sorted_runcat_ids = [entry['id'] for entry in sorted_runcat_ids]

        for idx, rcid in enumerate(sorted_runcat_ids):
            db_indices = db_queries.get_assoc_entries(self.database,
                                                                   rcid)
            py_indices = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            self.assertEqual(len(db_indices), len(py_indices))
            for nstep in range(len(db_indices)):
                for key in ('v_int', 'eta_int', 'f_datapoints'):
                    self.assertAlmostEqual(db_indices[nstep][key],
                                           py_indices[nstep][key])


@requires_database()
class TestInfiniteErrorFluxes(unittest.TestCase):
    """
    What happens if we perform a forced fit, it doesn't converge, and we
    get an 'infinite' error-bar? Do we handle this correctly?
    """
    @requires_database()
    def setUp(self):

        self.database = tkp.db.Database()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        self.database.close()

    def test_one2one_flux_infinite_error(self):
        dataset = tkp.db.DataSet(database=self.database, data={'description': 'flux test set: 1-1'})
        n_images = 3
        im_params = db_subs.generate_timespaced_dbimages_data(n_images)

        src_list = []
        src = db_subs.example_extractedsource_tuple()
        src0 = src._replace(flux=2.0)
        src_list.append(src0)
        src1 = src._replace(flux=2.5)
        src_list.append(src1)
        src2 = src._replace(flux=0.0001, flux_err=float('inf'),
                            peak=0.0001, peak_err=float('inf'))
        src_list.append(src2)

        for idx, im in enumerate(im_params):
            image = tkp.db.Image(database=self.database, dataset=dataset, data=im)
            image.insert_extracted_sources([src_list[idx]])
            associate_extracted_sources(image.id, deRuiter_r=3.717)

        query = """\
        SELECT rf.avg_f_int
              ,rf.f_datapoints
          FROM runningcatalog r
              ,runningcatalog_flux rf
        WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        """
        cursor = tkp.db.execute(query, {'dataset': dataset.id})
        results = db_subs.get_db_rows_as_dicts(cursor)

        self.assertEqual(len(results),1)

        self.assertEqual(results[0]['f_datapoints'],2)
        self.assertAlmostEqual(results[0]['avg_f_int'],
                               (src0.flux + src1.flux)/2.0 )


