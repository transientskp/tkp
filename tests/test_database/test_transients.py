import unittest2 as unittest
import tkp.db
from tkp.db.transients import multi_epoch_transient_search
from tkp.db.transients import _insert_transients
from tkp.db.generic import get_db_rows_as_dicts
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database


class TestTransientBasics(unittest.TestCase):

    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()

    def tearDown(self):
        tkp.db.rollback()

    def test_single_band_transient_search(self):
        """test_single_band_transient_search

            Test simplest functional case - only source is a transient source.
            This makes it simple to verify the database properties.

        """
        # We have to add a dataset, some images all with some measurements
        # After insertion, and source association, we run the transient search.
        dataset = tkp.db.DataSet(database=self.database,
                                data={'description':"Trans:"
                                        + self._testMethodName})
        n_images = 4
        im_params = db_subs.example_dbimage_datasets(n_images)

        TransientSource = db_subs.MockSource(
             ex=db_subs.example_extractedsource_tuple(),
             lightcurve=[
                 db_subs.MockLCPoint(index=2, peak=20e-2, flux=20e-2, sigma=200),
                 db_subs.MockLCPoint(index=3, peak=1e-2, flux=1e-2, sigma=10),
                    ]
                 )

        measurements = TransientSource.synthesise_measurements(
                                               n_images,
                                               include_non_detections=True)

        images = []
        for idx in range(len(im_params)):
            image = tkp.db.Image(dataset=dataset, data=im_params[idx])
            images.append(image)
            if measurements[idx] is not None:
                image.insert_extracted_sources([ measurements[idx] ])
            image.associate_extracted_sources(deRuiter_r=3.7)
            freq_bands = dataset.frequency_bands()
            self.assertEqual(len(freq_bands), 1)
            transients = multi_epoch_transient_search(
                                            eta_lim=1,
                                            V_lim=0.1,
                                            probability_threshold=0.7,
                                            minpoints=1,
                                            image_id=image.id)

        # Check the number of detected transients
        self.assertEqual(len(transients), 1)

        # Check that the bands for the images are the same as the transient's band
        freq_bands = dataset.frequency_bands()
        self.assertEqual(len(freq_bands), 1)
        for tr in transients:
            self.assertEqual(freq_bands[0], tr['band'])

        runcats = dataset.runcat_entries()
        self.assertEqual(len(runcats), 1)
        for tr in transients:
            self.assertEqual(runcats[0]['runcat'], tr['runcat'])

        # Check that the trigger xtrsrc happened in the third image
        query = """\
        select taustart_ts
          from extractedsource x
              ,image i
         where x.image = i.id
           and x.id = (select trigger_xtrsrc
                         from transient t
                             ,runningcatalog r
                        where t.runcat = r.id
                          and r.dataset = %s
                      )
        """
        self.database.cursor.execute(query, (dataset.id,))
        taustart_ts = zip(*self.database.cursor.fetchall())[0]
        self.assertEqual(len(taustart_ts), 1)
        ts = taustart_ts[0]
        self.assertEqual(ts, images[2].taustart_ts)

        # Check the variability indices, first eta_int:
        #query = """\
        #select sum((f_int - 0.06) * (f_int-0.06) / (f_int_err * f_int_err)) / 3
        #  from assocxtrsource a
        #      ,extractedsource x
        # where a.xtrsrc = x.id
        #   and a.runcat = 7
        #"""

        #FIXME: I'm not sure what this query is for?
        query = """\
        select sum((f_int - 0.06) * (f_int - 0.06) / (f_int_err * f_int_err)) / 3
          from assocxtrsource a
              ,extractedsource x
         where a.xtrsrc = x.id
           and a.runcat = (select t.runcat
                             from runningcatalog r
                                  ,transient t
                            where r.id = t.runcat
                              and r.dataset = %s
                          )
        """
        #self.assertAlmostEqual(1, 2)

class TestTransientRoutines(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(data={'description':"Trans:" +
                                                        self._testMethodName},
                                    database=self.database)

        self.n_images = 8
        self.im_params = db_subs.example_dbimage_datasets(self.n_images)
        self.db_imgs = []

        #Insert transient source extractions,
        #Include the non-detection points we expect from using monitoringlist:
        source_lists = db_subs.example_source_lists(n_images=8,
                                                  include_non_detections=True)
        for i in xrange(self.n_images):
            self.db_imgs.append(
                        tkp.db.Image(data=self.im_params[i],
                                            dataset=self.dataset)
                                )

            self.db_imgs[i].insert_extracted_sources(source_lists[i])
            self.db_imgs[i].associate_extracted_sources(deRuiter_r=3.7)

    def tearDown(self):
        tkp.db.rollback()

    def test_full_transient_search_routine(self):
        bands = self.dataset.frequency_bands()
        self.assertEqual(len(bands), 1)
        #First run with lax limits:
        transients = multi_epoch_transient_search(
                 eta_lim=1.1,
                 V_lim=0.01,
                 probability_threshold=0.01,
                 image_id=self.db_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(transients), 3)

        qry = """\
        SELECT tr.*
          FROM transient tr
              ,runningcatalog rc
          WHERE rc.dataset = %(dsid)s
            AND tr.runcat = rc.id
        """
        cursor = self.database.connection.cursor()
        cursor.execute(qry, {'dsid':self.dataset.id})
        transient_table_entries = get_db_rows_as_dicts(cursor)
        self.assertEqual(len(transient_table_entries), len(transients))
#        for t in all_transients:
#            print "V_int:", t['v_int'], "  eta_int:", t['eta_int']
        #Now test thresholding:
        more_highly_variable = sum(t['v_int'] > 2.0 for t in transients)
        very_non_flat = sum(t['eta_int'] > 100.0 for t in transients)

        transients = multi_epoch_transient_search(
                 eta_lim=1.1,
                 V_lim=2.0,
                 probability_threshold=0.01,
                 image_id=self.db_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(transients), more_highly_variable)

        transients = multi_epoch_transient_search(
                 eta_lim=100,
                 V_lim=0.01,
                 probability_threshold=0.01,
                 image_id=self.db_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(transients), very_non_flat)

    def test_variability_not_null(self):
        # As per #4306, it should be impossible to insert a transient with a
        # null value for V_int or eta_int.
        transients = [
            {'runcat': 0,
             'band': 0,
             'siglevel': 0,
             'v_int': None,
             'eta_int': None,
             'trigger_xtrsrc': 0}
        ]
        with self.assertRaises(self.database.exceptions.IntegrityError):
            _insert_transients(transients)
