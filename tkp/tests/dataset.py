import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
import sys
import datetime
import random
from operator import attrgetter, itemgetter
from utility.decorators import requires_database

# We're cheating here: a unit test shouldn't really depend on an
# external dependency like the database being up and running

class TestDataSet(unittest.TestCase):

    def setUp(self):
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        self.database = tkp.database.database.DataBase()

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_dataset_create(self):
        """Create a new dataset, and retrieve it"""
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        dataset1 = tkp.database.dataset.DataSet(
            'dataset 1', database=self.database)
        dsid = dataset1.dsid
        # The name for the following dataset will be ignored, and set
        # to the name of the dataset with dsid = dsid
        dataset2 = tkp.database.dataset.DataSet(
            dsid=dsid, database=self.database)
        # update some stuff
        self.assertEqual(dataset2.name, "dataset 1")
        self.assertEqual(dataset2.dsid, dsid)
        dataset2._set_data({
            'dsoutname': 'output.ms',
            'description': 'testing of dataset',
            'process_ts': datetime.datetime(1970, 1, 1)
            })
        self.assertEqual(dataset2.name, "dataset 1")
        self.assertEqual(dataset2.dsid, dsid)
        # the name is ignored if dsid is given:
        dataset3 = tkp.database.dataset.DataSet(
            'dataset 3', dsid=dsid, database=self.database)
        self.assertEqual(dataset3.name, "dataset 1")
        self.assertEqual(dataset3.dsid, dsid)

    @requires_database()
    def test_dataset_update(self):
        """Update all or individual dataset columns"""
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        dataset1 = tkp.database.dataset.DataSet(
            'dataset 1', database=self.database)
        self.assertEqual(dataset1.name, "dataset 1")
        dataset1.rerun = 0
        dataset1.dsinname = "new dataset"
        self.database.cursor.execute(
            "SELECT rerun, dsinname FROM datasets WHERE dsid=%s", (dataset1.dsid,))
        results = self.database.cursor.fetchone()
        self.assertEqual(results[0], 0)
        self.assertEqual(results[1], "new dataset")
        self.assertEqual(dataset1.name, "new dataset")

    @requires_database()
    def test_image_create(self):
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        dataset1 = tkp.database.dataset.DataSet(
            'dataset with images', database=self.database)
        self.assertEqual(dataset1.images, set())
        image1 = tkp.database.dataset.Image(
            dataset=dataset1)
        # Images are automatically added to their dataset
        self.assertEqual(dataset1.images, set([image1]))
        self.assertEqual(image1.tau_time, 0)
        self.assertAlmostEqual(image1.freq_eff, 0.)
        image2 = tkp.database.dataset.Image(
            dataset=dataset1)
        self.assertEqual(dataset1.images, set([image1, image2]))
        dataset2 = tkp.database.dataset.DataSet(
            database=self.database, dsid=dataset1.dsid)
        # Note that we can't test that dataset2.images = set([image1, image2]),
        # because dataset2.images are newly created Python objects,
        # with different ids
        self.assertEqual(len(dataset2.images), 2)

    @requires_database()
    def test_image_update(self):
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        dataset1 = tkp.database.dataset.DataSet(
            'dataset with changing images', database=self.database)
        data = dict(tau_time=1000, freq_eff=80e6)
        image1 = tkp.database.dataset.Image(
            dataset=dataset1, data=data)
        self.assertEqual(image1.tau_time, 1000.)
        self.assertAlmostEqual(image1.freq_eff, 80e6)
        image1.tau_time = 2000.
        self.assertEqual(image1.tau_time, 2000.)

        # New image, created from the database
        image2 = tkp.database.dataset.Image(
            dataset=dataset1, imageid=image1.imageid)
        self.assertEqual(image2.tau_time, 2000.)
        self.assertEqual(image2.freq_eff, 80e6)
        # Same id, so changing image2 changes image1
        # but *only* after calling update()
        image2.tau_time = 1500
        self.assertEqual(image1.tau_time, 2000.)
        image1.update()
        self.assertEqual(image1.tau_time, 1500.)
        image1.tau_time = 2500
        image2.update()
        self.assertEqual(image2.tau_time, 2500.)

    @requires_database()
    def test_source_create(self):
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        dataset1 = tkp.database.dataset.DataSet(
            'dataset with images', database=self.database)
        self.assertEqual(dataset1.images, set())
        image1 = tkp.database.dataset.Image(
            dataset=dataset1)
        image2 = tkp.database.dataset.Image(
            dataset=dataset1)
        data = {'ra': 123.123, 'decl': 23.23,
                'ra_err': 0.1, 'decl_err': 0.1}
        source1 = tkp.database.dataset.Source(
            image=image1, data=data)
        data['ra'] = 45.45
        data['decl'] = 55.55
        source2 = tkp.database.dataset.Source(
            image=image1, data=data)
        self.assertEqual(len(image1.sources), 2)
        # Source #3 points to the same source as #2
        source3 = tkp.database.dataset.Source(
            srcid=source2.srcid, database=self.database)
        # Which means there are no extra sources for image1
        self.assertEqual(len(image1.sources), 2)
        srcids = set([source.srcid for source in image1.sources])
        # If, however, we create a new source with
        # an image reference in the constructor, we get a
        # 'deep' copy:
        source4 = tkp.database.dataset.Source(
            image=image1, srcid=source2.srcid)
        # Now there's a new source for image1!
        self.assertEqual(len(image1.sources), 3)
        # But if we filter on the source ids,
        # we see there are really only two sources
        srcids = set([source.srcid for source in image1.sources])
        self.assertEqual(set([source1.srcid, source2.srcid]),
                         srcids)

        data['ra'] = 89.89
        data['decl'] = 78.78
        source5 = tkp.database.dataset.Source(
            image=image2, data=data)
        self.assertEqual(len(image2.sources), 1)
        self.assertEqual(image2.sources.pop().srcid, source5.srcid)

    @requires_database()
    def test_source_update(self):
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        dataset1 = tkp.database.dataset.DataSet(
            'dataset with images', database=self.database)
        self.assertEqual(dataset1.images, set())
        image1 = tkp.database.dataset.Image(
            dataset=dataset1)
        image2 = tkp.database.dataset.Image(
            dataset=dataset1)
        data = {'ra': 123.123, 'decl': 23.23,
                'ra_err': 0.1, 'decl_err': 0.1}
        source1 = tkp.database.dataset.Source(
            image=image1, data=data)
        data['ra'] = 45.45
        data['decl'] = 55.55
        source2 = tkp.database.dataset.Source(
            image=image1, data=data)
        self.assertEqual(len(image1.sources), 2)
        # Source #3 points to the same source as #2
        source3 = tkp.database.dataset.Source(
            srcid=source2.srcid, database=self.database)
        # Update source3
        source3.decl = 44.44
        # But no change for #1 and #2
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source2.decl, 55.55)
        self.assertAlmostEqual(source3.decl, 44.44)
        source1.update()  # nothing changes for #1
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source2.decl, 55.55)
        self.assertAlmostEqual(source3.decl, 44.44)
        source3.update()  # still no change
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source2.decl, 55.55)
        self.assertAlmostEqual(source3.decl, 44.44)
        # Now we make sure source #2 takes note of the change done through #3
        source2.update()
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source1.decl, 23.23)
        self.assertAlmostEqual(source2.decl, 44.44)

    @requires_database()
    def test_source_lightcurve(self):
        """This test serves more as an example than as a proper unit
        test"""
        import tkp.database.dataset
        import tkp.database.database
        import monetdb
        dataset = tkp.database.dataset.DataSet(
            'dataset with images', database=self.database)
        # create 4 images, separated by one day each
        images = [
            tkp.database.dataset.Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 3),
                      'tau_time': 3600}),
            tkp.database.dataset.Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 4),
                      'tau_time': 3600}),
            tkp.database.dataset.Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 5),
                      'tau_time': 3600}),
            tkp.database.dataset.Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 6),
                      'tau_time': 3600}),
            ]
        # 3 sources per image, with different coordinates & flux
        data_list = [dict(ra=111.111*i, decl=11.11*i,
                          ra_err=0.01, decl_err=0.01,
                          i_peak=10*i, i_peak_err=0.1)
                     for i in range(1, 4)]
        # Insert the 3 sources in each image, while further varying the flux
        for i, image in enumerate(images):
            # Create the "source finding results"
            sources = [
                (data['ra'], data['decl'], data['ra_err'], data['decl_err'],
                 data['i_peak']*(1+i), data['i_peak_err'],
                 data['i_peak']*(1+i), data['i_peak_err'], 10.)
                for data in data_list]
            # Insert the sources
            image.insert_extracted_sources(sources)
            # Run the association for each list of source for an image
            image.associate_extracted_sources()

        # updates the dataset, and thereby list of sources for each image
        dataset.update()
        # Now pick any image, select the first source (smallest RA)
        # and extract its light curve
        sources = dataset.images.pop().sources
        sources = sorted(sources, key=attrgetter('ra'))
        lightcurve = sources[0].lightcurve()
        self.assertEqual(lightcurve[0][0], datetime.datetime(2010, 3, 3, 0, 0))
        self.assertEqual(lightcurve[1][0], datetime.datetime(2010, 3, 4, 0, 0))
        self.assertEqual(lightcurve[2][0], datetime.datetime(2010, 3, 5, 0, 0))
        self.assertEqual(lightcurve[3][0], datetime.datetime(2010, 3, 6, 0, 0))
        self.assertAlmostEqual(lightcurve[0][2], 10.)
        self.assertAlmostEqual(lightcurve[1][2], 20.)
        self.assertAlmostEqual(lightcurve[2][2], 30.)
        self.assertAlmostEqual(lightcurve[3][2], 40.)

        # Since the light curve are very similar, only eta_nu is different
        results = dataset.detect_variables()
        results = sorted(results, key=itemgetter('eta_nu'))
        for result, eta_nu in zip(results, (12500.0, 50000.0, 112500.0)):
            self.assertEqual(result['npoints'], 4)
            self.assertAlmostEqual(result['eta_nu'], eta_nu)
            self.assertAlmostEqual(result['v_nu'], 0.516397779494)


if __name__ == "__main__":
    unittest.main()
