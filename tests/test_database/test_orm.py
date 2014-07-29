import unittest

import datetime
from tkp.testutil.decorators import requires_database
import tkp.db
from tkp.db.orm import DataSet, Image
from tkp.db.database import Database
from tkp.db.orm import ExtractedSource
from tkp.testutil import db_subs

# We're cheating here: a unit test shouldn't really depend on an
# external dependency like the database being up and running


class TestDataSet(unittest.TestCase):

    def setUp(self):
        self.database = Database()

    def tearDown(self):
        tkp.db.rollback()

    @requires_database()
    def test_create(self):
        """Create a new dataset, and retrieve it"""
        dataset1 = DataSet(data={'description': 'dataset 1'})
        # The name for the following dataset will be ignored, and set
        # to the name of the dataset with dsid = dsid
        dataset2 = DataSet(id=dataset1.id)
        # update some stuff
        dataset2.update()
        self.assertEqual(dataset2.description, "dataset 1")
        self.assertEqual(dataset2.id, dataset1.id)
        self.assertEqual(dataset2.description, "dataset 1")
        self.assertEqual(dataset2.id, dataset1.id)
        # 'data' is ignored if dsid is given:
        dataset3 = DataSet(data={'description': 'dataset 3'}, id=dataset1.id)
        self.assertEqual(dataset3.description, "dataset 1")
        self.assertEqual(dataset3.id, dataset1.id)

    @requires_database()
    def test_update(self):
        """Update all or individual dataset columns"""
        dataset1 = DataSet(data={'description': 'dataset 1'}, )
        self.assertEqual(dataset1.description, "dataset 1")
        dataset1.update(rerun=5, description="new dataset")
        self.database.cursor.execute(
            "SELECT rerun, description FROM dataset WHERE id=%s", (dataset1.id,))
        results = self.database.cursor.fetchone()
        self.assertEqual(results[0], 5)
        self.assertEqual(results[1], "new dataset")
        self.assertEqual(dataset1.description, "new dataset")
        self.assertEqual(dataset1.rerun, 5)
        dataset1.update(process_end_ts=datetime.datetime(1970, 1, 1))
        self.assertEqual(
            dataset1.process_end_ts, datetime.datetime(1970, 1, 1)
        )


class TestImage(unittest.TestCase):

    def setUp(self):
        import tkp.db.database
        self.database = tkp.db.database.Database()

    def tearDown(self):
        tkp.db.rollback()

    @requires_database()
    def test_create(self):
        image_data_dicts = db_subs.generate_timespaced_dbimages_data(n_images=2)
        dataset1 = DataSet(data={'description': 'dataset with images'},
                           database=self.database)
        #self.assertEqual(dataset1.images, set())
        image1 = Image(dataset=dataset1, data=image_data_dicts[0])
        # Images are automatically added to their dataset
        #self.assertEqual(dataset1.images, set([image1]))
        self.assertEqual(image1.tau_time, image_data_dicts[0]['tau_time'])
        self.assertAlmostEqual(image1.freq_eff, image_data_dicts[0]['freq_eff'])
        image2 = Image(dataset=dataset1, data=image_data_dicts[1])
        #self.assertEqual(dataset1.images, set([image1, image2]))
        dataset2 = DataSet(database=self.database, id=dataset1.id)
        # Note that we can't test that dataset2.images = set([image1, image2]),
        # because dataset2.images are newly created Python objects,
        # with different ids
        #self.assertEqual(len(dataset2.images), 2)





    @requires_database()
    def test_infinite(self):
        # Check that database insertion doesn't choke on infinite beam
        # parameters.
        test_specific_image_data = {'beam_smaj_pix': float('inf'),
                                    'beam_smin_pix': float('inf'),
                                    'beam_pa_rad': float('inf'),}

        image_data_dicts = db_subs.generate_timespaced_dbimages_data(n_images=1,
                                              **test_specific_image_data)
        image_data = image_data_dicts[0]

        dataset1 = DataSet(data={'description': 'dataset with images'},
                           database=self.database)
        image1 = Image(dataset=dataset1, data=image_data)
        bmaj, bmin, bpa = tkp.db.execute("""
            SELECT rb_smaj, rb_smin, rb_pa
            FROM image
            WHERE image.id = %(id)s
        """, {"id": image1.id}).fetchone()
        self.assertEqual(bmaj, float('inf'))
        self.assertEqual(bmin, float('inf'))
        self.assertEqual(bpa, float('inf'))


    @requires_database()
    def test_update(self):
        """
        Check that ORM-updates work for the Image class.
        """

        dataset1 = DataSet(data={'description':
                                  'dataset with changing images'},
                                  database=self.database)
        image_data = db_subs.example_dbimage_data_dict()

        image1 = Image(dataset=dataset1, data=image_data)
        # Now, update (without changing anything) and make sure it remains the
        # same (sanity check):
        image1.update()
        self.assertEqual(image1.tau_time, image_data['tau_time'])

        ##This time, change something:
        tau_time1 = image_data['tau_time'] + 100
        tau_time2 = tau_time1 + 300
        tau_time3 = tau_time2 + 300
        tau_time4 = tau_time3 + 300

        freq_eff1 = image_data['freq_eff']*1.2

        image1.update(tau_time = tau_time1)
        self.assertEqual(image1.tau_time, tau_time1)


        # New 'image' orm-object, created from the database id of image1.
        image2 = Image(dataset=dataset1, id=image1.id)
        self.assertAlmostEqual(image2.tau_time, tau_time1)
        self.assertAlmostEqual(image2.freq_eff, image_data['freq_eff'])
        # Same id, so changing image2 changes image1
        # but *only* after calling update()
        image2.update(tau_time=tau_time2)
        self.assertAlmostEqual(image1.tau_time, tau_time1)
        image1.update()
        self.assertAlmostEqual(image1.tau_time, tau_time2)
        image1.update(tau_time=tau_time3)
        image2.update()
        self.assertAlmostEqual(image2.tau_time, tau_time3)
        #Test with multiple items:
        image1.update(tau_time=tau_time4, freq_eff=freq_eff1)
        self.assertAlmostEqual(image1.tau_time, tau_time4)
        self.assertAlmostEqual(image1.freq_eff, freq_eff1)

        #And that datetime conversion roundtrips work correctly:
        dtime0 = image_data['taustart_ts']
        dtime1 = dtime0 + datetime.timedelta(days=3)
        self.assertEqual(image1.taustart_ts, dtime0)
        self.assertEqual(image2.taustart_ts, dtime0)
        image2.update(taustart_ts=dtime1)
        #image1 orm-object not yet updated, still caches old value:
        self.assertEqual(image1.taustart_ts, dtime0)
        self.assertEqual(image2.taustart_ts, dtime1)
        image1.update()
        self.assertEqual(image1.taustart_ts, dtime1)


class TestExtractedSource(unittest.TestCase):

    def setUp(self):
        import tkp.db.database
        self.database = tkp.db.database.Database()

    def tearDown(self):
        tkp.db.rollback()

    @requires_database()
    def test_infinite(self):
        # Check that database insertion doesn't choke on infinite errors
        dataset = DataSet(data={'description': 'example dataset'},
                           database=self.database)
        image = Image(dataset=dataset, data=db_subs.example_dbimage_data_dict())

        # Inserting an example extractedsource should be fine
        extracted_source = db_subs.example_extractedsource_tuple()
        image.insert_extracted_sources([extracted_source])

        # But it should also be fine if the source has infinite errors
        extracted_source = db_subs.example_extractedsource_tuple(error_radius=float('inf'),
                                                                 peak_err=float('inf'),
                                                                 flux_err=float('inf'))
        image.insert_extracted_sources([extracted_source])

    @requires_database()
    def test_create(self):

        dataset = DataSet(data={'description': 'dataset with images'},
                          database=self.database)
        # create 4 images, separated by one day each
        image = Image(
                dataset=dataset,
                data=db_subs.example_dbimage_data_dict())
        extracted_source_data = dict(zone=13,
                    ra=12.12, decl=13.13, ra_err=21.1, decl_err=21.09,
                    ra_fit_err=1.12, decl_fit_err=1.23,
                    uncertainty_ew=0.1,uncertainty_ns=0.1,
                    ew_sys_err=20, ns_sys_err=20,
                    error_radius=10.0,
                    x=0.11, y=0.22, z=0.33,
                    racosdecl=0.44, det_sigma=10.)
        src1 = ExtractedSource(data=extracted_source_data, image=image)
        src2 = ExtractedSource(data=extracted_source_data, image=image, database=self.database)
        self.assertNotEqual(src1.id, src2.id)

        extracted_source_data['image'] = image.id
        src3 = ExtractedSource(data=extracted_source_data, database=self.database)
        extracted_source_data['ra'] = 23.23
        src4 = ExtractedSource(data=extracted_source_data, database=self.database, id=src1.id)
        self.assertEqual(src1.id, src4.id)
        self.assertAlmostEqual(src1.ra, src4.ra)
        del extracted_source_data['x']
        self.assertRaisesRegexp(
            AttributeError, "missing required data key: x",
            ExtractedSource, data=extracted_source_data, database=self.database)

    @requires_database()
    def test_create2(self):

        dataset1 = DataSet(data={'description': 'dataset with images'},
                                 database=self.database)
        self.assertEqual(dataset1.images, set())
        image_data = db_subs.example_dbimage_data_dict()
        image1 = Image(dataset=dataset1, data=image_data)
        image2 = Image(dataset=dataset1, data=image_data)

        extractedsource_data = {'ra': 123.123, 'decl': 23.23,
                'ra_err': 21.1, 'decl_err': 21.09,
                'ra_fit_err': 0.1, 'decl_fit_err': 0.1,
                'uncertainty_ew': 0.1, 'uncertainty_ns': 0.1,
                'zone': 1, 'x': 0.11, 'y': 0.22, 'z': 0.33,
                'racosdecl': 0.44,
                'det_sigma': 10.0,
                'ew_sys_err': 20, 'ns_sys_err': 20,
                'error_radius': 10.0}
        source1 = ExtractedSource(image=image1, data=extractedsource_data)
        extractedsource_data['ra'] = 45.45
        extractedsource_data['decl'] = 55.55
        source2 = ExtractedSource(
            image=image1, data=extractedsource_data)
        self.assertEqual(len(image1.sources), 2)
        # Source #3 points to the same source as #2
        source3 = ExtractedSource(id=source2.id, database=self.database)
        # Which means there are no extra sources for image1
        self.assertEqual(len(image1.sources), 2)
        srcids = set([source.id for source in image1.sources])
        # If, however, we create a new source with
        # an image reference in the constructor, we get a
        # 'deep' copy:
        source4 = ExtractedSource(image=image1, id=source2.id)
        # Now there's a new source for image1!
        self.assertEqual(len(image1.sources), 3)
        # But if we filter on the source ids,
        # we see there are really only two sources
        srcids = set([source.id for source in image1.sources])
        self.assertEqual(set([source1.id, source2.id]), srcids)

        extractedsource_data['ra'] = 89.89
        extractedsource_data['decl'] = 78.78
        source5 = ExtractedSource(image=image2, data=extractedsource_data)
        self.assertEqual(len(image2.sources), 1)
        self.assertEqual(image2.sources.pop().id, source5.id)


    @requires_database()
    def test_update(self):
        image_data = db_subs.example_dbimage_data_dict()
        dataset1 = DataSet(data={'description': 'dataset with images'},
                           database=self.database)
        self.assertEqual(dataset1.images, set())
        image1 = Image(dataset=dataset1, data=image_data)
        image2 = Image(dataset=dataset1, data=image_data)
        extractedsource_data = {'ra': 123.123, 'decl': 23.23,
                'ra_err': 21.1, 'decl_err': 21.09,
                'ra_fit_err': 0.1, 'decl_fit_err': 0.1,
                'uncertainty_ew': 0.1, 'uncertainty_ns': 0.1,
                'zone': 1, 'x': 0.11, 'y': 0.22, 'z': 0.33,
                'racosdecl': 0.44,
                'det_sigma': 11.1,
                'ew_sys_err': 20, 'ns_sys_err': 20,
                'error_radius': 10.0}
        source1 = ExtractedSource(image=image1, data=extractedsource_data)
        extractedsource_data['ra'] = 45.45
        extractedsource_data['decl'] = 55.55
        source2 = ExtractedSource(image=image1, data=extractedsource_data)
        self.assertEqual(len(image1.sources), 2)
        # Source #3 points to the same source as #2
        source3 = ExtractedSource(id=source2.id, database=self.database)
        # Update source3
        source3.update(decl=44.44)
        # But no change for #1 and #2
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source2.decl, 55.55)
        self.assertAlmostEqual(source3.decl, 44.44)
        source1.update()  # nothing changes for #1
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source2.decl, 55.55)
        self.assertAlmostEqual(source3.decl, 44.44)
        # Now we make sure source #2 takes note of the change done through #3
        source2.update()
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source2.decl, 44.44)


if __name__ == "__main__":
    unittest.main()
