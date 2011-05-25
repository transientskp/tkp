import unittest
import sys
import datetime
import monetdb
import tkp.database.dataset
import tkp.database.database



# We're cheating here: a unit test shouldn't really depend on an
# external dependency like the database up and running

class TestDataSet(unittest.TestCase):

    def setUp(self):
        try:
            self.database = tkp.database.database.DataBase()
        except monetdb.monetdb_exceptions.DatabaseError, exc:
            self.database = None

    def tearDown(self):
        if self.database:
            self.database.close()
        
    def test_dataset_create(self):
        """Create a new dataset, and retrieve it"""
        if not self.database:
            self.skipTest("Database not available.")
        dataset1 = tkp.database.dataset.DataSet(
            'dataset 1', database=self.database)
        dsid = dataset1.dsid
        # The name for the following dataset will be ignored, and set
        # to the name of the dataset with dsid = dsid
        dataset2 = tkp.database.dataset.DataSet(
            'dataset 2', dsid=dsid, database=self.database)
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
        
    def test_dataset_update(self):
        """Update all or individual dataset columns"""
        if not self.database:
            self.skipTest("Database not available.")
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

    def test_image_create(self):
        if not self.database:
            self.skipTest("Database not available.")
        dataset1 = tkp.database.dataset.DataSet(
            'dataset with images', database=self.database)
        self.assertEqual(dataset1.images, [])
        image1 = tkp.database.dataset.Image(
            dataset=dataset1)
        # Images are automatically added to their dataset
        self.assertEqual(dataset1.images, [image1])
        self.assertEqual(image1.tau_time, 0)
        self.assertAlmostEqual(image1.freq_eff, 0.)
        image2 = tkp.database.dataset.Image(
            dataset=dataset1)
        self.assertEqual(dataset1.images, [image1, image2])
        dataset2 = tkp.database.dataset.DataSet(
            database=self.database, dsid=dataset1.dsid)
        # Note that we can't test that dataset2.images = [image1, image2],
        # because dataset2.images are newly created Python objects,
        # with different ids
        self.assertEqual(len(dataset2.images), 2)

    def test_image_update(self):
        if not self.database:
            self.skipTest("Database not available.")
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

        
        
if __name__ == "__main__":
    unittest.main()
