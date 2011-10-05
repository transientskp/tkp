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
        import tkp.database.database
        self.database = tkp.database.database.DataBase()

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_create(self):
        """Create a new dataset, and retrieve it"""
        from tkp.database.dataset import DataSet
        import tkp.database.database
        import monetdb
        dataset1 = DataSet(data={'dsinname': 'dataset 1'},
                           database=self.database)
        dsid = dataset1.id
        # The name for the following dataset will be ignored, and set
        # to the name of the dataset with dsid = dsid
        dataset2 = DataSet(database=self.database, id=dsid)
        # update some stuff
        dataset2.update()
        self.assertEqual(dataset2.dsinname, "dataset 1")
        self.assertEqual(dataset2.id, dsid)
        dataset2.update(dsoutname='output.ms',
                        description='testing of dataset',
                        process_ts=datetime.datetime(1970, 1, 1))
        self.assertEqual(dataset2.dsinname, "dataset 1")
        self.assertEqual(dataset2.id, dsid)
        # 'data' is ignored if dsid is given:
        dataset3 = DataSet(data={'dsinname': 'dataset 3'},
                           id=dsid, database=self.database)
        self.assertEqual(dataset3.dsinname, "dataset 1")
        self.assertEqual(dataset3.id, dsid)

    @requires_database()
    def test_update(self):
        """Update all or individual dataset columns"""
        from tkp.database.dataset import DataSet
        import tkp.database.database
        import monetdb
        dataset1 = DataSet(data={'dsinname': 'dataset 1'},
                            database=self.database)
        self.assertEqual(dataset1.dsinname, "dataset 1")
        dataset1.update(rerun=5, dsinname="new dataset")
        self.database.cursor.execute(
            "SELECT rerun, dsinname FROM datasets WHERE dsid=%s", (dataset1.id,))
        results = self.database.cursor.fetchone()
        self.assertEqual(results[0], 5)
        self.assertEqual(results[1], "new dataset")
        self.assertEqual(dataset1.dsinname, "new dataset")
        self.assertEqual(dataset1.rerun, 5)


class TestImage(unittest.TestCase):

    def setUp(self):
        import tkp.database.database
        self.database = tkp.database.database.DataBase()

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_create(self):
        from tkp.database.dataset import DataSet
        from tkp.database.dataset import Image
        import tkp.database.database
        import monetdb
        data = {
            'freq_eff': 80e6,
            'freq_bw': 1e6,
            'taustart_ts': datetime.datetime(1999, 9, 9),
            'url': '/path/to/image',
            'tau_time': 0,
            }
        dataset1 = DataSet(data={'dsinname': 'dataset with images'},
                           database=self.database)
        #self.assertEqual(dataset1.images, set())
        image1 = Image(dataset=dataset1, data=data)
        # Images are automatically added to their dataset
        #self.assertEqual(dataset1.images, set([image1]))
        self.assertEqual(image1.tau_time, 0)
        self.assertAlmostEqual(image1.freq_eff, 80e6)
        image2 = Image(dataset=dataset1, data=data)
        #self.assertEqual(dataset1.images, set([image1, image2]))
        dataset2 = DataSet(database=self.database, id=dataset1.id)
        # Note that we can't test that dataset2.images = set([image1, image2]),
        # because dataset2.images are newly created Python objects,
        # with different ids
        #self.assertEqual(len(dataset2.images), 2)

    @requires_database()
    def test_update(self):
        from tkp.database.dataset import DataSet
        from tkp.database.dataset import Image
        import tkp.database.database
        import monetdb
        dataset1 = DataSet(data={'dsinname':
                                  'dataset with changing images'},
                                  database=self.database)
        data = dict(tau_time=1000, freq_eff=80e6,
                    url='/',
                    taustart_ts=datetime.datetime(2001, 1, 1),
                    freq_bw=1e6)
        image1 = Image(dataset=dataset1, data=data)
        self.assertAlmostEqual(image1.tau_time, 1000.)
        self.assertAlmostEqual(image1.freq_eff, 80e6)
        image1.update(tau_time=2000.)
        self.assertAlmostEqual(image1.tau_time, 2000.)

        # New image, created from the database
        image2 = Image(dataset=dataset1, id=image1.id)
        self.assertAlmostEqual(image2.tau_time, 2000.)
        self.assertAlmostEqual(image2.freq_eff, 80e6)
        # Same id, so changing image2 changes image1
        # but *only* after calling update()
        image2.update(tau_time=1500)
        self.assertAlmostEqual(image1.tau_time, 2000)
        image1.update()
        self.assertAlmostEqual(image1.tau_time, 1500)
        image1.update(tau_time=2500)
        image2.update()
        self.assertAlmostEqual(image2.tau_time, 2500)
        image1.update(tau_time=1000., freq_eff=90e6)
        self.assertAlmostEqual(image1.tau_time, 1000)
        self.assertAlmostEqual(image1.freq_eff, 90e6)
        self.assertEqual(image1.taustart_ts, datetime.datetime(2001, 1, 1))
        self.assertEqual(image2.taustart_ts, datetime.datetime(2001, 1, 1))
        image2.update(taustart_ts=datetime.datetime(2010, 3, 3))
        self.assertEqual(image1.taustart_ts, datetime.datetime(2001, 1, 1))
        self.assertEqual(image2.taustart_ts, datetime.datetime(2010, 3, 3))
        self.assertAlmostEqual(image2.tau_time, 1000)
        self.assertAlmostEqual(image2.freq_eff, 90e6)
        image1.update()
        self.assertEqual(image1.taustart_ts, datetime.datetime(2010, 3, 3))


class TestExtractedSource(unittest.TestCase):

    def setUp(self):
        import tkp.database.database
        self.database = tkp.database.database.DataBase()

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_create(self):
        from tkp.database.dataset import DataSet
        from tkp.database.dataset import Image
        from tkp.database.dataset import ExtractedSource
        dataset = DataSet(data={'dsinname': 'dataset with images'},
                          database=self.database)
        # create 4 images, separated by one day each
        image = Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 3),
                      'tau_time': 3600,
                      'url': '/',
                      'freq_eff': 80e6,
                      'freq_bw': 1e6})
        data = dict(zone=1, ra=12.12, decl=13.13, ra_err=1.12, decl_err=1.23,
                    x=0.11, y=0.22, z=0.33, det_sigma=10.)
        src1 = ExtractedSource(data=data, image=image)
        src2 = ExtractedSource(data=data, image=image, database=self.database)
        data['image_id'] = image.id
        src3 = ExtractedSource(data=data, database=self.database)
        data['ra'] = 23.23
        src4 = ExtractedSource(data=data, database=self.database, id=src1.id)
        self.assertEqual(src1.id, src4.id)
        self.assertAlmostEqual(src1.ra, src4.ra)
        del data['x']
        self.assertRaisesRegexp(
            AttributeError, "missing required data key: x",
            ExtractedSource, data=data, database=self.database)

    @requires_database()
    def test_create2(self):
        from tkp.database.dataset import DataSet
        from tkp.database.dataset import Image
        from tkp.database.dataset import ExtractedSource
        import tkp.database.database
        import monetdb
        data = {
            'freq_eff': 80e6,
            'freq_bw': 1e6,
            'taustart_ts': datetime.datetime(1999, 9, 9),
            'url': '/path/to/image',
            'tau_time': 0,
                }
        dataset1 = DataSet(data={'dsinname': 'dataset with images'},
                                 database=self.database)
        self.assertEqual(dataset1.images, set())
        image1 = Image(dataset=dataset1, data=data)
        image2 = Image(dataset=dataset1, data=data)

        data = {'ra': 123.123, 'decl': 23.23,
                'ra_err': 0.1, 'decl_err': 0.1,
                'zone': 1, 'x': 0.11, 'y': 0.22, 'z': 0.33,
                'det_sigma': 10.0}
        source1 = ExtractedSource(image=image1, data=data)
        data['ra'] = 45.45
        data['decl'] = 55.55
        source2 = ExtractedSource(
            image=image1, data=data)
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

        data['ra'] = 89.89
        data['decl'] = 78.78
        source5 = ExtractedSource(image=image2, data=data)
        self.assertEqual(len(image2.sources), 1)
        self.assertEqual(image2.sources.pop().id, source5.id)


    @requires_database()
    def test_update(self):
        from tkp.database.dataset import DataSet
        from tkp.database.dataset import Image
        from tkp.database.dataset import ExtractedSource
        import tkp.database.database
        import monetdb
        data = {
            'freq_eff': 80e6,
            'freq_bw': 1e6,
            'taustart_ts': datetime.datetime(1999, 9, 9),
            'url': '/path/to/image',
            'tau_time': 0,
                }
        dataset1 = DataSet(data={'dsinname': 'dataset with images'},
                           database=self.database)
        self.assertEqual(dataset1.images, set())
        image1 = Image(dataset=dataset1, data=data)
        image2 = Image(dataset=dataset1, data=data)
        data = {'ra': 123.123, 'decl': 23.23,
                'ra_err': 0.1, 'decl_err': 0.1,
                'zone': 1, 'x': 0.11, 'y': 0.22, 'z': 0.33,
                'det_sigma': 11.1}
        source1 = ExtractedSource(image=image1, data=data)
        data['ra'] = 45.45
        data['decl'] = 55.55
        source2 = ExtractedSource(image=image1, data=data)
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

    @requires_database()
    def test_lightcurve(self):
        """This test serves more as an example than as a proper unit
        test"""
        from tkp.database.dataset import DataSet
        from tkp.database.dataset import Image
        from tkp.database.dataset import ExtractedSource
        import tkp.database.database
        import monetdb
        dataset = DataSet(data={'dsinname': 'dataset with images'},
                          database=self.database)
        # create 4 images, separated by one day each
        images = [
            Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 3),
                      'tau_time': 3600,
                      'url': '/',
                      'freq_eff': 80e6,
                      'freq_bw': 1e6}),
            Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 4),
                      'tau_time': 3600,
                      'url': '/',
                      'freq_eff': 80e6,
                      'freq_bw': 1e6}),
            Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 5),
                      'tau_time': 3600,
                      'url': '/',
                      'freq_eff': 80e6,
                      'freq_bw': 1e6}),
            Image(
                dataset=dataset,
                data={'taustart_ts': datetime.datetime(2010, 3, 6),
                      'tau_time': 3600,
                      'url': '/',
                      'freq_eff': 80e6,
                      'freq_bw': 1e6}),
            ]
        # 3 sources per image, with different coordinates & flux
        data_list = [dict(ra=111.111*i, decl=11.11*i,
                          ra_err=0.01, decl_err=0.01,
                          i_peak=10*i, i_peak_err=0.1,
#                          x=0.11, y=0.22, z=0.33, det_sigma=11.1,
#                          zone=i
                          )
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

        # updates the dataset and its set of images
        dataset.update()
        dataset.update_images()
        # update the images and their sets of sources
        for image in dataset.images: 
            image.update()
            image.update_sources()
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

        # Since the light curves are very similar, only eta_nu is different
        results = dataset.detect_variables()
        results = sorted(results, key=itemgetter('eta_nu'))
        for result, eta_nu in zip(results, (16666.66666667, 66666.666666667,
                                            150000.0)):
            self.assertEqual(result['npoints'], 4)
            self.assertAlmostEqual(result['eta_nu'], eta_nu)
            self.assertAlmostEqual(result['v_nu'], 0.516397779494)
    
        
if __name__ == "__main__":
    unittest.main()
