import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import tkp.database as tkpdb
import tkp.database.utils.transients as dbt
import tkp.database.utils as dbutils
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database, duration


class TestTransientBasics(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.database = tkpdb.DataBase()
    def tearDown(self):
        self.database.close()

    def test_single_band_transient_search(self):
        """test_single_band_transient_search

            Test simplest functional case - only source is a transient source.
            This makes it simple to verify the database properties.

        """
        # We have to add a dataset, some images all with some measurements
        # After insertion, and source association, we run the transient search.
        dataset = tkpdb.DataSet(database=self.database,
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
            images.append(tkpdb.Image(dataset=dataset, data=im_params[idx]))
            if measurements[idx] is not None:
                images[-1].insert_extracted_sources([ measurements[idx] ])
            images[-1].associate_extracted_sources()
            freq_bands = dataset.frequency_bands()
            self.assertEqual(len(freq_bands), 1)
            transient_ids, siglevels, transients = dbt.transient_search(
                                            conn=self.database.connection,
                                            dsid=dataset.id,
                                            freq_band=freq_bands[0],
                                            eta_lim=1,
                                            V_lim=0.1,
                                            probability_threshold=0.7,
                                            minpoints=1,
                                            imageid=images[-1].id)
            #print "transient_ids:",transient_ids
            #print "siglevels:",siglevels

        # Check the number of detected transients
        self.assertEqual(len(transients), 1)

        # Check that the bands for the images are the same as the transient's band
        freq_bands = dataset.frequency_bands()
        self.assertEqual(len(freq_bands), 1)
        for tr in transients:
            self.assertEqual(freq_bands[0], tr.band)

        runcats = dataset.runcat_entries()
        self.assertEqual(len(runcats), 1)
        for tr in transients:
            print "tr.siglevel:", tr.siglevel
            self.assertEqual(runcats[0]['runcat'], tr.runcatid)

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
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(data={'description':"Trans:" +
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
                        tkpdb.Image(data=self.im_params[i],
                                            dataset=self.dataset)
                                )

            self.db_imgs[i].insert_extracted_sources(source_lists[i])
            self.db_imgs[i].associate_extracted_sources(deRuiter_r=3.7)

    def tearDown(self):
        self.database.close()

    def test_full_transient_search_routine(self):
        bands = self.dataset.frequency_bands()
        self.assertEqual(len(bands), 1)
        transient_ids, siglevels, transients = dbutils.transient_search(
                 conn=self.database.connection,
                 dsid=self.dataset.id,
                 freq_band=bands[0],
                 eta_lim=1.1,
                 V_lim=0.01,
                 probability_threshold=0.01,
                 imageid=self.db_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(transients), 3)
